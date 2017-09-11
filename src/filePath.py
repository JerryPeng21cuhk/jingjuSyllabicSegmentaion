from os.path import join, dirname

# audio and annotation root path
root_path       = join(dirname(__file__),'..')

# nacta 2017 dataset part 2
nacta2017_dataset_root_path     = '/Users/gong/Documents/MTG document/Jingju arias/jingju_a_cappella_singing_dataset_extended_nacta2017'

# nacta dataset part 1
nacta_dataset_root_path     = '/Users/gong/Documents/MTG document/Jingju arias/jingju_a_cappella_singing_dataset'

nacta2017_wav_path = join(nacta2017_dataset_root_path, 'wav')
nacta2017_textgrid_path = join(nacta2017_dataset_root_path, 'textgridDianSilence')
nacta2017_score_path = join(nacta2017_dataset_root_path, 'scoreDianSilence')

nacta_wav_path = join(nacta_dataset_root_path, 'wav')
nacta_textgrid_path = join(nacta_dataset_root_path, 'textgrid')
nacta_score_path = '/Users/gong/Documents/github/MTG/JingjuSingingAnnotation/aCapella/Syllable duration annotation'

eval_results_path = join(root_path, 'output')

from parameters import mth_ODF, fusion, layer2, filter_shape

cnnModels_path  = join(root_path, 'cnnModels')

if mth_ODF == 'jan':
    filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jan_class_weight_mfccBands_2D_all_optim.h5'
    cnnModel_name         = 'jan_cw'
elif mth_ODF == 'jan_chan3':
    filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jan_class_weight_3_chans_mfccBands_2D_all_optim.h5'
    # filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jan_class_weight_3_chans_layer1_70_mfccBands_2D_all_optim.h5'
    # filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jan_no_class_weight_mfccBands_2D_all_optim.h5'
    cnnModel_name           = 'jan_cw_3_chans'
elif mth_ODF == 'jordi_horizontal_timbral':
    if layer2 == 20:
        filename_keras_cnn_0 = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_horizontal_timbral_filter_layer2_20_mfccBands_2D_all_optim.h5'
        cnnModel_name        = 'jordi_cw_conv_dense_horizontal_timbral_filter_layer2_20'
    else:
        filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_horizontal_timbral_filter_mfccBands_2D_all_optim.h5'
        cnnModel_name         = 'jordi_cw_conv_dense_horizontal_timbral_filter'
else:
    # mth_ODF == 'jordi'
    if fusion:
        if layer2 == 20:
            filename_keras_cnn_0 = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_layer2_20_mfccBands_2D_all_optim.h5'
            filename_keras_cnn_1 = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_timbral_filter_layer2_20_mfccBands_2D_all_optim.h5'
            cnnModel_name        = 'jordi_cw_conv_dense_horizontal_timbral_filter_late_fusion_multiply_layer2_20'
        else:
            filename_keras_cnn_0 = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_mfccBands_2D_all_optim.h5'
            filename_keras_cnn_1 = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_timbral_filter_mfccBands_node04_2D_all_optim.h5'
            cnnModel_name        = 'jordi_cw_conv_dense_horizontal_timbral_filter_late_fusion_multiply'
    else:
        if filter_shape == 'temporal':
            # filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jordi_class_weight_mfccBands_2D_all_optim.h5'
            # filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jordi_class_weight_with_dense_mfccBands_2D_all_optim.h5'
            if layer2 == 20:
                filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_layer2_20_mfccBands_2D_all_optim.h5'
                cnnModel_name           = 'jordi_cw_conv_dense_layer2_20'
            else:
                # layer2 32 nodes
                filename_keras_cnn_0    = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_mfccBands_2D_all_optim.h5'
                # filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_149k_mfccBands_2D_all_optim.h5'
                # filename_keras_cnn_1  = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_second_model_32_mfccBands_2D_all_optim.h5'
                cnnModel_name           = 'jordi_cw_conv_dense'
        else:
            # timbral filter shape
            if layer2 == 20:
                filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_timbral_filter_layer2_20_mfccBands_2D_all_optim.h5'
                cnnModel_name           = 'jordi_cw_conv_dense_timbral_filter_layer2_20'
            else:
                # layer2 32 nodes
                filename_keras_cnn_0  = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_timbral_filter_mfccBands_node04_2D_all_optim.h5'
                # filename_keras_cnn_0 = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_timbral_filter_152k_mfccBands_2D_all_optim.h5'
                # filename_keras_cnn_1 = 'keras.cnn_syllableSeg_jordi_class_weight_with_conv_dense_timbral_filter_second_model_32_mfccBands_2D_all_optim.h5'
                cnnModel_name          = 'jordi_cw_conv_dense_horizontal_timbral_filter'

filename_scaler_onset    = 'scaler_syllable_mfccBands2D.pkl'
filename_scaler_onset_23 = 'scaler_syllable_mfccBands2D_23.pkl'
filename_scaler_onset_46 = 'scaler_syllable_mfccBands2D_46.pkl'
filename_scaler_onset_93 = 'scaler_syllable_mfccBands2D_93.pkl'


full_path_keras_cnn_0                   = join(cnnModels_path, filename_keras_cnn_0)

if fusion and mth_ODF == 'jordi':
    full_path_keras_cnn_1                   = join(cnnModels_path, filename_keras_cnn_1)

full_path_mfccBands_2D_scaler_onset     = join(cnnModels_path, filename_scaler_onset)

full_path_mfccBands_2D_scaler_onset_23     = join(cnnModels_path, filename_scaler_onset_23)
full_path_mfccBands_2D_scaler_onset_46     = join(cnnModels_path, filename_scaler_onset_46)
full_path_mfccBands_2D_scaler_onset_93     = join(cnnModels_path, filename_scaler_onset_93)


# Evaluation path
# cnnModel_name           = 'jan_cw'
# cnnModel_name           = 'jan_cw_3_chans'
# cnnModel_name           = 'jan_cw_3_chans_layer1_70'
# cnnModel_name           = 'jan_ncw'
# cnnModel_name           = 'jordi_cw'
# cnnModel_name           = 'jordi_ncw'
# cnnModel_name           = 'jordi_cw_dense'
# cnnModel_name           = 'jordi_cw_conv_dense'
# cnnModel_name           = 'jordi_cw_conv_dense_149k'

# cnnModel_name           = 'jordi_cw_conv_dense_layer2_20'

# cnnModel_name           = 'jordi_cw_conv_dense_timbral_filter'
# cnnModel_name           = 'jordi_cw_conv_dense_timbral_filter_152k'
# cnnModel_name           = 'jordi_cw_conv_dense_timbral_filter_layer2_20'
# cnnModel_name           = 'jordi_cw_conv_dense_timbral_filter_late_fusion_2_models_multiply'

# cnnModel_name           = 'jordi_cw_conv_dense_horizontal_timbral_filter'
# cnnModel_name           = 'jordi_cw_conv_dense_horizontal_timbral_filter_layer2_20'

# cnnModel_name           = 'jordi_cw_conv_dense_horizontal_filter_late_fusion_2_models_multiply'
# cnnModel_name           = 'jordi_cw_conv_dense_horizontal_timbral_filter_late_fusion_multiply_layer2_20'

decoding_method         = '_win'

# eval_results_path       = join(root_path, 'eval', 'results', cnnModel_name+decoding_method)
# eval_fig_path           = join(root_path, 'eval', 'figs', cnnModel_name+decoding_method)


# acoustic model name and path
filename_scaler_am                      = 'scaler_syllableSeg_am_mfccBands2D.pkl'
full_path_mfccBands_2D_scaler_am        = join(cnnModels_path, 'am', filename_scaler_am)
filename_keras_cnn_am                   = 'keras.cnn_syllableSeg_am_mfccBands_2D_all_optim.h5'
full_path_keras_cnn_am                  = join(cnnModels_path, 'am', filename_keras_cnn_am)