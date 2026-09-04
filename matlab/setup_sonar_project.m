% Run this file once after opening the project in MATLAB.
% It makes the MATLAB source folder available and sets a stable working folder.

matlab_dir = fileparts(mfilename('fullpath'));
project_root = fileparts(matlab_dir);

addpath(matlab_dir);
cd(project_root);

fprintf('AUV Sonar MATLAB project configured.\n');
fprintf('  Project root: %s\n', project_root);
fprintf('  MATLAB path:  %s\n', matlab_dir);
fprintf('Next, run: run_profile_evaluation_tests\n');
