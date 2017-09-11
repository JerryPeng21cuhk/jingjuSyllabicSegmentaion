# -*- coding: utf-8 -*-
import pickle
from os import makedirs, walk, listdir
from os.path import isfile, exists, dirname, join

import essentia.standard as ess
import numpy as np
from keras.models import load_model

import pyximport
pyximport.install(reload_support=True,
                  setup_args={'include_dirs': np.get_include()})

from src.filePath import *
from src.labWriter import boundaryLabWriter
from src.parameters import *
from src.scoreManip import phonemeDurationForLine
from src.scoreParser import generatePinyin
from src.textgridParser import textGrid2WordList, wordListsParseByLines
from trainingSampleCollection import featureReshape
from trainingSampleCollection import getMFCCBands2D


import viterbiDecoding
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches



def getOnsetFunction(observations, path_keras_cnn, method='jan'):
    """
    Load CNN model to calculate ODF
    :param observations:
    :return:
    """

    model = load_model(path_keras_cnn)

    ##-- call pdnn to calculate the observation from the features
    if method=='jordi':
        observations = [observations, observations, observations, observations, observations, observations]
    elif method=='jordi_horizontal_timbral':
        observations = [observations, observations, observations, observations, observations, observations,
                        observations, observations, observations, observations, observations, observations]

    obs = model.predict_proba(observations, batch_size=128)
    return obs


def featureExtraction(audio_monoloader, scaler, framesize, dmfcc=False, nbf=False, feature_type='mfccBands2D'):
    """
    extract mfcc features
    :param audio_monoloader:
    :param scaler:
    :param dmfcc:
    :param nbf:
    :param feature_type:
    :return:
    """
    if feature_type == 'mfccBands2D':
        mfcc = getMFCCBands2D(audio_monoloader, framesize, nbf=nbf, nlen=varin['nlen'])
        mfcc = np.log(100000 * mfcc + 1)

        mfcc = np.array(mfcc, dtype='float32')
        mfcc_scaled = scaler.transform(mfcc)
        mfcc_reshaped = featureReshape(mfcc_scaled)
    else:
        print(feature_type + ' is not exist.')
        raise
    return mfcc, mfcc_reshaped


def trackOnsetPosByPath(path, idx_syllable_start_state):
    idx_onset = []
    for ii in range(len(path)-1):
        if path[ii+1] != path[ii] and path[ii+1] in idx_syllable_start_state:
            idx_onset.append(ii)
    return idx_onset

def late_fusion_calc(obs_0, obs_1, mth=0, coef=0.5):
    """
    Late fusion methods
    :param obs_0:
    :param obs_1:
    :param mth: 0-addition 1-addition with linear norm 2-exponential weighting mulitplication with linear norm
    3-multiplication 4- multiplication with linear norm
    :param coef: weighting coef for multiplication
    :return:
    """
    assert len(obs_0) == len(obs_1)

    obs_out = []

    if mth==1 or mth==2 or mth==4:
        from sklearn.preprocessing import MinMaxScaler
        min_max_scaler = MinMaxScaler()
        obs_0 = obs_0.reshape((len(obs_0),1))
        obs_1 = obs_1.reshape((len(obs_1),1))
        # print(obs_0.shape, obs_1.shape)
        obs_0 = min_max_scaler.fit_transform(obs_0)
        obs_1 = min_max_scaler.fit_transform(obs_1)

    if mth == 0 or mth == 1:
        # addition
        obs_out = np.add(obs_0, obs_1)/2
    elif mth == 2:
        # multiplication with exponential weighting
        obs_out = np.multiply(np.power(obs_0, coef), np.power(obs_1, 1-coef))
    elif mth == 3 or mth == 4:
        # multiplication
        obs_out = np.multiply(obs_0, obs_1)

    return obs_out


def onsetFunctionAllRecordings(wav_path,
                               textgrid_path,
                               score_path,
                               feature_type='mfcc',
                               dmfcc=False,
                               nbf=True,
                               mth='jordi',
                               late_fusion=True):
    """
    ODF and viter decoding
    :param recordings:
    :param textgrid_path:
    :param dataset_path:
    :param feature_type: 'mfcc', 'mfccBands1D' or 'mfccBands2D'
    :param dmfcc: delta for 'mfcc'
    :param nbf: context frames
    :param mth: jordi, jordi_horizontal_timbral, jan, jan_chan3
    :param late_fusion: Bool
    :return:
    """

    scaler = pickle.load(open(full_path_mfccBands_2D_scaler_onset, 'rb'))
    if mth == 'jan_chan3':
        scaler_23 = pickle.load(open(full_path_mfccBands_2D_scaler_onset_23, 'rb'))
        scaler_46 = pickle.load(open(full_path_mfccBands_2D_scaler_onset_46, 'rb'))
        scaler_93 = pickle.load(open(full_path_mfccBands_2D_scaler_onset_93, 'rb'))

    # kerasModel = _LRHMM.kerasModel(full_path_keras_cnn_am)

    list_file_path_name = []
    for file_path_name in walk(score_path):
        list_file_path_name.append(file_path_name)

    list_artist_level_path = list_file_path_name[0][1]


    for artist_path in list_artist_level_path:
        textgrid_artist_path = join(textgrid_path, artist_path)
        recording_names = [f for f in listdir(textgrid_artist_path) if isfile(join(textgrid_artist_path, f))]
        print(recording_names)


        for rn in recording_names:
            rn = rn.split('.')[0]

            groundtruth_textgrid_file   = join(textgrid_path, artist_path, rn+'.TextGrid')
            score_file                  = join(score_path, artist_path, rn+'.csv')
            wav_file                    = join(wav_path, artist_path, rn+'.wav')

            if not isfile(score_file):
                print 'Score not found: ' + score_file
                continue

            lineList        = textGrid2WordList(groundtruth_textgrid_file, whichTier='line')


            # parse score
            syllables, pinyins, syllable_durations, bpm = generatePinyin(score_file)

            # print(pinyins)
            # print(syllable_durations)

            # load audio
            audio_monoloader               = ess.MonoLoader(downmix = 'left', filename = wav_file, sampleRate = fs)()
            audio_eqloudloder              = ess.EqloudLoader(filename=wav_file, sampleRate = fs)()

            if mth == 'jordi' or mth == 'jordi_horizontal_timbral' or mth == 'jan':
                mfcc, mfcc_reshaped = featureExtraction(audio_monoloader,
                                                              scaler,
                                                              int(round(0.025 * fs)),
                                                              dmfcc=dmfcc,
                                                              nbf=nbf,
                                                              feature_type='mfccBands2D')
            elif mth == 'jan_chan3':
                # for jan 3 channels input
                mfcc_23, mfcc_reshaped_23 = featureExtraction(audio_monoloader,
                                                        scaler_23,
                                                        int(round(0.023 * fs)),
                                                        dmfcc=dmfcc,
                                                        nbf=nbf,
                                                        feature_type='mfccBands2D')

                mfcc_46, mfcc_reshaped_46 = featureExtraction(audio_monoloader,
                                                        scaler_46,
                                                        int(round(0.046 * fs)),
                                                        dmfcc=dmfcc,
                                                        nbf=nbf,
                                                        feature_type='mfccBands2D')

                mfcc_93, mfcc_reshaped_93 = featureExtraction(audio_monoloader,
                                                        scaler_93,
                                                        int(round(0.093 * fs)),
                                                        dmfcc=dmfcc,
                                                        nbf=nbf,
                                                        feature_type='mfccBands2D')

            # print lineList
            i_line = 0
            for i_obs, line in enumerate(lineList):
                if len(line[2]) == 0:
                    continue

                # if int(bpm[i_obs]) == 0:
                #     continue

                try:
                    print(syllables[i_line])
                except:
                    continue

                sample_start    = int(round(line[0] * fs))
                sample_end      = int(round(line[1] * fs))
                frame_start     = int(round(line[0] * fs / hopsize))
                frame_end       = int(round(line[1] * fs / hopsize))
                # print(feature.shape)

                if mth == 'jordi' or mth == 'jordi_horizontal_timbral' or mth == 'jan':
                    audio_eqloudloder_line = audio_eqloudloder[sample_start:sample_end]
                    mfcc_line          = mfcc[frame_start:frame_end]
                    mfcc_reshaped_line = mfcc_reshaped[frame_start:frame_end]
                elif mth == 'jan_chan3':
                    mfcc_line_23 = mfcc_23[frame_start:frame_end]
                    mfcc_reshaped_line_23 = mfcc_reshaped_23[frame_start:frame_end]
                    mfcc_reshaped_line_23 = mfcc_reshaped_line_23[...,np.newaxis]

                    mfcc_line_46 = mfcc_46[frame_start:frame_end]
                    mfcc_reshaped_line_46 = mfcc_reshaped_46[frame_start:frame_end]
                    mfcc_reshaped_line_46 = mfcc_reshaped_line_46[...,np.newaxis]

                    mfcc_line_93 = mfcc_93[frame_start:frame_end]
                    mfcc_reshaped_line_93 = mfcc_reshaped_93[frame_start:frame_end]
                    mfcc_reshaped_line_93 = mfcc_reshaped_line_93[...,np.newaxis]

                    mfcc_reshaped_line = np.concatenate((mfcc_reshaped_line_23,mfcc_reshaped_line_46,mfcc_reshaped_line_93),axis=3)

                obs     = getOnsetFunction(observations=mfcc_reshaped_line,
                                           path_keras_cnn=full_path_keras_cnn_0,
                                           method=mth)
                obs_i   = obs[:,1]

                hann = np.hanning(5)
                hann /= np.sum(hann)

                obs_i = np.convolve(hann, obs_i, mode='same')

                if late_fusion:
                    obs_2 = getOnsetFunction(observations=mfcc_reshaped_line,
                                             path_keras_cnn=full_path_keras_cnn_1,
                                             method=mth)
                    obs_2_i = obs_2[:, 1]
                    obs_2_i = np.convolve(hann, obs_2_i, mode='same')
                    obs_i = late_fusion_calc(obs_i, obs_2_i, mth=2)

                obs_i = np.squeeze(obs_i)
                # organize score
                print('Calculating: '+rn+' phrase '+str(i_obs))
                print('ODF Methods: '+mth_ODF+' Late fusion: '+str(fusion))

                time_line      = line[1] - line[0]

                lyrics_line    = line[2]

                print('Syllable:')
                print(lyrics_line)

                pinyin_score   = pinyins[i_line]
                pinyin_score   = [ps for ps in pinyin_score if len(ps)]
                duration_score = syllable_durations[i_line]
                duration_score = np.array([float(ds) for ds in duration_score if len(ds)])
                duration_score = duration_score * (time_line/np.sum(duration_score))

                # segmental decoding
                obs_i[0] = 1.0
                obs_i[-1] = 1.0
                # print(duration_score)

                i_boundary = viterbiDecoding.viterbiSegmental2(obs_i, duration_score, varin)

                time_boundray_start = np.array(i_boundary[:-1])*hopsize_t
                time_boundray_end   = np.array(i_boundary[1:])*hopsize_t

                # uncomment this section if we want to write boundaries to .syll.lab file
                filename_syll_lab = join(eval_results_path, artist_path, rn+'_'+str(i_line+1)+'.syll.lab')

                eval_results_data_path = dirname(filename_syll_lab)

                if not exists(eval_results_data_path):
                    makedirs(eval_results_data_path)

                # write boundary lab file
                boundaryLabWriter(boundaryList=zip(time_boundray_start.tolist(),time_boundray_end.tolist(),filter(None,pinyins[i_line])),
                                  outputFilename=filename_syll_lab,
                                    label=True)

                i_line += 1

                # print(i_boundary)
                # print(len(obs_i))
                # print(np.array(groundtruth_syllable)*fs/hopsize)
                #
                #
                # # plot Error analysis figures
                # plt.figure(figsize=(16, 6))
                # # plt.figure(figsize=(8, 4))
                # # class weight
                # ax1 = plt.subplot(3,1,1)
                # y = np.arange(0, 80)
                # x = np.arange(0, mfcc_line.shape[0])*(hopsize/float(fs))
                # cax = plt.pcolormesh(x, y, np.transpose(mfcc_line[:, 80 * 11:80 * 12]))
                # for gs in groundtruth_syllable:
                #     plt.axvline(gs, color='r', linewidth=2)
                # # cbar = fig.colorbar(cax)
                # ax1.set_ylabel('Mel bands', fontsize=12)
                # ax1.get_xaxis().set_visible(False)
                # ax1.axis('tight')
                # plt.title('Calculating: '+recording_name+' phrase '+str(i_obs))
                #
                # ax2 = plt.subplot(312, sharex=ax1)
                # plt.plot(np.arange(0,len(obs_i))*(hopsize/float(fs)), obs_i)
                # for ib in i_boundary:
                #     plt.axvline(ib * (hopsize / float(fs)), color='r', linewidth=2)
                #
                # ax2.set_ylabel('ODF', fontsize=12)
                # ax2.axis('tight')
                #
                #
                # ax3 = plt.subplot(313, sharex=ax1)
                # print(duration_score)
                # time_start = 0
                # for ii_ds, ds in enumerate(duration_score):
                #     ax3.add_patch(
                #         patches.Rectangle(
                #             (time_start, ii_ds),  # (x,y)
                #             ds,  # width
                #             1,  # height
                #         ))
                #     time_start += ds
                # ax3.set_ylim((0,len(duration_score)))
                # # plt.xlabel('Time (s)')
                # # plt.tight_layout()
                #
                # plt.show()


if __name__ == '__main__':


    # Queen Mary female
    onsetFunctionAllRecordings(wav_path=wav_path,
                               textgrid_path=textgrid_path,
                               score_path=score_path,
                               feature_type='mfccBands2D',
                               dmfcc=False,
                               nbf=True,
                               mth=mth_ODF,
                               late_fusion=fusion)