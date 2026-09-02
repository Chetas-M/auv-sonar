% ==============================================================================
% File: export_c_headers.m
% Description: Exports 12-bit DAC lookup tables as firmware-ready prototype C
% header files for STM32G4 microcontroller bring-up.
% ==============================================================================

function export_c_headers(output_dir)
    if nargin < 1
        output_dir = fullfile(pwd, 'outputs_matlab', 'headers');
    end
    if ~exist(output_dir, 'dir')
        mkdir(output_dir);
    end

    cfg = config_sonar();
    profiles = profile_definitions();

    % 1. Export each individual profile header
    for i = 1:length(profiles)
        p = profiles(i);
        [wf, ~] = generate_lfm_chirp(p.f_start_hz, p.f_end_hz, p.duration_s, cfg.Fs, 1.0);
        [dac_codes, quant_metrics] = dac_quantize(wf.signal, cfg);

        file_path = fullfile(output_dir, p.header_file);
        write_single_header(file_path, p, wf, dac_codes, quant_metrics, cfg);
        fprintf('  [+] Exported: %s\n', file_path);
    end

    % 2. Export master registry header
    master_path = fullfile(output_dir, 'sonar_profiles.h');
    write_master_header(master_path, profiles);
    fprintf('  [+] Exported master registry: %s\n', master_path);
end

function write_single_header(filepath, profile, wf, dac_codes, quant_metrics, cfg)
    fid = fopen(filepath, 'w');
    if fid == -1
        error('Cannot open file for writing: %s', filepath);
    end

    guard = upper(strrep(profile.header_file, '.', '_'));
    sample_count = length(dac_codes);
    byte_count = sample_count * 2;

    fprintf(fid, '/**\n');
    fprintf(fid, ' * @file    %s\n', profile.header_file);
    fprintf(fid, ' * @brief   Firmware-Ready Prototype 12-bit DAC Lookup Table for %s Sonar Chirp\n', profile.name);
    fprintf(fid, ' * @target  %s (Timer TRGO -> DMA -> high-speed STM32G4 DAC path, verified during board bring-up)\n', cfg.target_mcu);
    fprintf(fid, ' *\n');
    fprintf(fid, ' * @section METADATA\n');
    fprintf(fid, ' * - Profile Mode:           %s\n', profile.name);
    fprintf(fid, ' * - DAC Sample Rate:         %u Hz (4.0 MSPS)\n', uint32(cfg.Fs));
    fprintf(fid, ' * - Start Frequency (f_0):   %.1f Hz\n', profile.f_start_hz);
    fprintf(fid, ' * - End Frequency (f_1):     %.1f Hz\n', profile.f_end_hz);
    fprintf(fid, ' * - Center Frequency (f_c):  %.1f Hz\n', profile.f_center_hz);
    fprintf(fid, ' * - Bandwidth (B):           %.1f Hz\n', profile.bandwidth_hz);
    fprintf(fid, ' * - Pulse Duration:          %.3f ms\n', profile.duration_s * 1000.0);
    fprintf(fid, ' * - Total Samples:           %u\n', uint32(sample_count));
    fprintf(fid, ' * - Memory Footprint:        %u bytes (%.2f KB)\n', uint32(byte_count), byte_count / 1024.0);
    fprintf(fid, ' * - DAC Bit Depth:           12-bit unsigned (0 to 4095)\n');
    fprintf(fid, ' * - Window Function:         Hann\n');
    fprintf(fid, ' * - Simulated SQNR:          %.2f dB\n', quant_metrics.sqnr_db);
    fprintf(fid, ' *\n');
    fprintf(fid, ' * @note PROTOTYPE FIRMWARE LUT: Requires physical verification on STM32G4 bench hardware.\n');
    fprintf(fid, ' *       At 4.0 MSPS, external analog buffering and high-speed DAC mode must be confirmed on scope.\n');
    fprintf(fid, ' */\n\n');

    fprintf(fid, '#ifndef %s_\n', guard);
    fprintf(fid, '#define %s_\n\n', guard);
    fprintf(fid, '#include <stdint.h>\n\n');
    fprintf(fid, '#ifdef __cplusplus\nextern "C" {\n#endif\n\n');

    fprintf(fid, '/* DMA 32-bit alignment helper */\n');
    fprintf(fid, '#ifndef DMA_ALIGN\n');
    fprintf(fid, '  #if defined(__GNUC__) || defined(__clang__)\n');
    fprintf(fid, '    #define DMA_ALIGN __attribute__((aligned(4)))\n');
    fprintf(fid, '  #else\n');
    fprintf(fid, '    #define DMA_ALIGN\n');
    fprintf(fid, '  #endif\n');
    fprintf(fid, '#endif\n\n');

    fprintf(fid, '#define %s_SAMPLE_RATE_HZ  (%uUL)\n', profile.lut_name, uint32(cfg.Fs));
    fprintf(fid, '#define %s_F_START_HZ      (%uUL)\n', profile.lut_name, uint32(profile.f_start_hz));
    fprintf(fid, '#define %s_F_END_HZ        (%uUL)\n', profile.lut_name, uint32(profile.f_end_hz));
    fprintf(fid, '#define %s_DURATION_US     (%uUL)\n', profile.lut_name, uint32(profile.duration_s * 1e6));
    fprintf(fid, '#define %s_SAMPLE_COUNT    (%uU)\n', profile.lut_name, uint32(sample_count));
    fprintf(fid, '#define %s_SIZE_BYTES      (%uU)\n\n', profile.lut_name, uint32(byte_count));

    fprintf(fid, 'DMA_ALIGN const uint16_t %s[%u] = {\n', profile.lut_name, uint32(sample_count));

    % Format samples: 16 samples per line in 0x0FFF format
    for idx = 1:sample_count
        if mod(idx - 1, 16) == 0
            fprintf(fid, '    ');
        end
        fprintf(fid, '0x%04X', dac_codes(idx));
        if idx < sample_count
            fprintf(fid, ', ');
        end
        if mod(idx, 16) == 0 || idx == sample_count
            fprintf(fid, '\n');
        end
    end

    fprintf(fid, '};\n\n');
    fprintf(fid, '#ifdef __cplusplus\n}\n#endif\n\n');
    fprintf(fid, '#endif /* %s_ */\n', guard);

    fclose(fid);
end

function write_master_header(filepath, profiles)
    fid = fopen(filepath, 'w');
    if fid == -1
        error('Cannot open master header for writing: %s', filepath);
    end

    fprintf(fid, '/**\n');
    fprintf(fid, ' * @file    sonar_profiles.h\n');
    fprintf(fid, ' * @brief   Master header registering all adaptive chirp lookup tables for STM32G4.\n');
    fprintf(fid, ' * @note    PROTOTYPE HEADER: For firmware bring-up and descriptor lookup.\n');
    fprintf(fid, ' */\n\n');

    fprintf(fid, '#ifndef SONAR_PROFILES_H_\n');
    fprintf(fid, '#define SONAR_PROFILES_H_\n\n');
    fprintf(fid, '#include <stdint.h>\n');
    fprintf(fid, '#include <stddef.h>\n');
    for i = 1:length(profiles)
        fprintf(fid, '#include "%s"\n', profiles(i).header_file);
    end
    fprintf(fid, '\n#ifdef __cplusplus\nextern "C" {\n#endif\n\n');

    fprintf(fid, 'typedef enum {\n');
    fprintf(fid, '    SONAR_PROFILE_MUDDY = 0,     /**< 100-220 kHz for turbid/degraded channel */\n');
    fprintf(fid, '    SONAR_PROFILE_BALANCED = 1,  /**< 200-400 kHz nominal default */\n');
    fprintf(fid, '    SONAR_PROFILE_CLEAR = 2,     /**< 350-500 kHz for high resolution clear water */\n');
    fprintf(fid, '    SONAR_PROFILE_COUNT\n');
    fprintf(fid, '} SonarProfileId_t;\n\n');

    fprintf(fid, 'typedef struct {\n');
    fprintf(fid, '    SonarProfileId_t profile_id;\n');
    fprintf(fid, '    const char*      name;\n');
    fprintf(fid, '    uint32_t         sample_rate_hz;\n');
    fprintf(fid, '    uint32_t         f_start_hz;\n');
    fprintf(fid, '    uint32_t         f_end_hz;\n');
    fprintf(fid, '    uint32_t         duration_us;\n');
    fprintf(fid, '    uint16_t         sample_count;\n');
    fprintf(fid, '    uint16_t         size_bytes;\n');
    fprintf(fid, '    const uint16_t*  waveform_lut;\n');
    fprintf(fid, '} SonarProfileDescriptor_t;\n\n');

    fprintf(fid, 'static const SonarProfileDescriptor_t SONAR_PROFILES[SONAR_PROFILE_COUNT] = {\n');
    for i = 1:length(profiles)
        p = profiles(i);
        fprintf(fid, '    {\n');
        fprintf(fid, '        .profile_id     = (SonarProfileId_t)%d,\n', i - 1);
        fprintf(fid, '        .name           = "%s",\n', p.name);
        fprintf(fid, '        .sample_rate_hz = %s_SAMPLE_RATE_HZ,\n', p.lut_name);
        fprintf(fid, '        .f_start_hz     = %s_F_START_HZ,\n', p.lut_name);
        fprintf(fid, '        .f_end_hz       = %s_F_END_HZ,\n', p.lut_name);
        fprintf(fid, '        .duration_us    = %s_DURATION_US,\n', p.lut_name);
        fprintf(fid, '        .sample_count   = %s_SAMPLE_COUNT,\n', p.lut_name);
        fprintf(fid, '        .size_bytes     = %s_SIZE_BYTES,\n', p.lut_name);
        fprintf(fid, '        .waveform_lut   = %s\n', p.lut_name);
        if i < length(profiles)
            fprintf(fid, '    },\n');
        else
            fprintf(fid, '    }\n');
        end
    end
    fprintf(fid, '};\n\n');

    fprintf(fid, '#ifdef __cplusplus\n}\n#endif\n\n');
    fprintf(fid, '#endif /* SONAR_PROFILES_H_ */\n');

    fclose(fid);
end
