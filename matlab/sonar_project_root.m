function project_root = sonar_project_root()
%SONAR_PROJECT_ROOT Return the repository root independently of MATLAB's pwd.
    matlab_dir = fileparts(mfilename('fullpath'));
    project_root = fileparts(matlab_dir);
end
