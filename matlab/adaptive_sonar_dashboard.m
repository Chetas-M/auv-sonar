function adaptive_sonar_dashboard
% ADAPTIVE_SONAR_DASHBOARD
% Live MATLAB dashboard for the SIH 26058 adaptive sonar concept.
%
% NOTE:
% The profile viability rules below include both integration with the official
% digital twin propagation model (evaluate_profile_performance) and a lightweight
% fallback demonstration rule set.

%% -------------------- Initial values --------------------
S.range = 145;          % m
S.temperature = 20;     % deg C
S.salinity = 35;        % PSU
S.turbidity = "Moderate";
S.mission = "Survey";

updateTimer = [];

%% -------------------- Create UI --------------------------
fig = uifigure( ...
    'Name','Adaptive Sonar Dashboard', ...
    'Position',[100 100 900 600], ...
    'Color',[0.96 0.96 0.96], ...
    'CloseRequestFcn',@(~,~)onClose());

main = uigridlayout(fig,[1 2]);
main.ColumnWidth = {'1.2x','2x'};
main.RowHeight = {'1x'};
main.Padding = [15 15 15 15];
main.ColumnSpacing = 15;

%% -------------------- Left: controls ---------------------
controlPanel = uipanel(main,'Title','Simulation Controls');
controlPanel.FontWeight = 'bold';

g = uigridlayout(controlPanel,[9 2]);
g.RowHeight = {30,45,30,30,30,30,30,30,40};
g.ColumnWidth = {130,'1x'};
g.Padding = [12 12 12 12];

uilabel(g,'Text','Range (m):','FontWeight','bold');
rangeEdit = uieditfield(g,'numeric','Value',S.range, ...
    'Limits',[1 1000],'RoundFractionalValues',false);

uilabel(g,'Text','Range slider:','FontWeight','bold');
rangeSlider = uislider(g,'Limits',[1 1000],'Value',S.range);

uilabel(g,'Text','Temperature (°C):','FontWeight','bold');
tempEdit = uieditfield(g,'numeric','Value',S.temperature);

uilabel(g,'Text','Salinity (PSU):','FontWeight','bold');
salEdit = uieditfield(g,'numeric','Value',S.salinity);

uilabel(g,'Text','Turbidity:','FontWeight','bold');
turbDrop = uidropdown(g,'Items',{'Low','Moderate','High'}, ...
    'Value',S.turbidity);

uilabel(g,'Text','Mission mode:','FontWeight','bold');
missionDrop = uidropdown(g,'Items',{'Survey','Search','Tracking'}, ...
    'Value',S.mission);

uilabel(g,'Text','Update rate:','FontWeight','bold');
rateDrop = uidropdown(g,'Items',{'On change','1 Hz','2 Hz','5 Hz'}, ...
    'Value','On change');

uilabel(g,'Text','Current profile:','FontWeight','bold');
profileLamp = uilamp(g,'Color',[0.2 0.7 0.2]);

updateButton = uibutton(g,'Text','UPDATE DASHBOARD', ...
    'ButtonPushedFcn',@(~,~)updateDashboard(), ...
    'FontWeight','bold');

resetButton = uibutton(g,'Text','RESET', ...
    'ButtonPushedFcn',@(~,~)resetDashboard());

%% -------------------- Right: dashboard -------------------
dashPanel = uipanel(main,'Title','Adaptive Sonar Dashboard');
dashPanel.FontWeight = 'bold';

d = uigridlayout(dashPanel,[13 2]);
d.RowHeight = {35,28,28,28,28,15,28,28,28,28,28,28,'1x'};
d.ColumnWidth = {190,'1x'};
d.Padding = [15 15 15 15];

titleLabel = uilabel(d,'Text','Adaptive Sonar Dashboard', ...
    'FontSize',18,'FontWeight','bold');
titleLabel.Layout.Column = [1 2];

rangeLabel = uilabel(d,'Text','Range:');
rangeValue = uilabel(d,'Text','');
rangeValue.FontWeight = 'bold';

tempLabel = uilabel(d,'Text','Temperature:');
tempValue = uilabel(d,'Text','');

salLabel = uilabel(d,'Text','Salinity:');
salValue = uilabel(d,'Text','');

turbLabel = uilabel(d,'Text','Turbidity:');
turbValue = uilabel(d,'Text','');

uilabel(d,'Text',''); % spacer
uilabel(d,'Text','');

lowText = uilabel(d,'Text','LOW (100-220 kHz):');
lowValue = uilabel(d,'Text','');
lowValue.FontWeight = 'bold';

balancedText = uilabel(d,'Text','BALANCED (200-400 kHz):');
balancedValue = uilabel(d,'Text','');
balancedValue.FontWeight = 'bold';

highText = uilabel(d,'Text','HIGH (350-500 kHz):');
highValue = uilabel(d,'Text','');
highValue.FontWeight = 'bold';

missionLabel = uilabel(d,'Text','Mission Mode:');
missionValue = uilabel(d,'Text','');

selectedLabel = uilabel(d,'Text','Selected Profile:');
selectedValue = uilabel(d,'Text','');
selectedValue.FontWeight = 'bold';

confidenceLabel = uilabel(d,'Text','Confidence:');
confidenceValue = uilabel(d,'Text','');

statusLabel = uilabel(d,'Text','Status');
statusLabel.FontWeight = 'bold';
statusValue = uilabel(d,'Text','');
statusValue.FontWeight = 'bold';

%% -------------------- Callbacks ---------------------------
rangeEdit.ValueChangedFcn = @(~,~)syncFromEdit();
rangeSlider.ValueChangedFcn = @(~,~)syncFromSlider();
tempEdit.ValueChangedFcn = @(~,~)updateDashboard();
salEdit.ValueChangedFcn = @(~,~)updateDashboard();
turbDrop.ValueChangedFcn = @(~,~)updateDashboard();
missionDrop.ValueChangedFcn = @(~,~)updateDashboard();
rateDrop.ValueChangedFcn = @(~,~)changeUpdateRate();

%% -------------------- Initial update ----------------------
updateDashboard();

%% ==================== Nested functions ===================

    function syncFromEdit()
        value = max(rangeEdit.Limits(1), min(rangeEdit.Limits(2), rangeEdit.Value));
        rangeEdit.Value = value;
        rangeSlider.Value = min(rangeSlider.Limits(2), max(rangeSlider.Limits(1), value));
        updateDashboard();
    end

    function syncFromSlider()
        rangeEdit.Value = rangeSlider.Value;
        updateDashboard();
    end

    function changeUpdateRate()
        val = string(rateDrop.Value);
        if isempty(updateTimer) || ~isvalid(updateTimer)
            updateTimer = timer('ExecutionMode', 'fixedRate', ...
                                'TimerFcn', @(~,~)updateDashboard(), ...
                                'Name', 'AdaptiveSonarDashboardTimer');
        end
        if strcmp(updateTimer.Running, 'on')
            stop(updateTimer);
        end
        switch val
            case "1 Hz"
                updateTimer.Period = 1.0;
                start(updateTimer);
            case "2 Hz"
                updateTimer.Period = 0.5;
                start(updateTimer);
            case "5 Hz"
                updateTimer.Period = 0.2;
                start(updateTimer);
            case "On change"
                % Timer remains stopped
        end
    end

    function onClose()
        if ~isempty(updateTimer) && isvalid(updateTimer)
            if strcmp(updateTimer.Running, 'on')
                stop(updateTimer);
            end
            delete(updateTimer);
        end
        delete(fig);
    end

    function resetDashboard()
        rangeEdit.Value = 145;
        rangeSlider.Value = 145;
        tempEdit.Value = 20;
        salEdit.Value = 35;
        turbDrop.Value = "Moderate";
        missionDrop.Value = "Survey";
        rateDrop.Value = "On change";
        changeUpdateRate();
        updateDashboard();
    end

    function updateDashboard()
        % Read current inputs
        S.range = rangeEdit.Value;
        S.temperature = tempEdit.Value;
        S.salinity = salEdit.Value;
        S.turbidity = turbDrop.Value;
        S.mission = missionDrop.Value;

        % Evaluate profile viability and selection.
        if exist('evaluate_profile_performance', 'file') == 2
            switch S.turbidity
                case "Low"
                    turb_ntu = 0.0;
                case "Moderate"
                    turb_ntu = 50.0;
                case "High"
                    turb_ntu = 100.0;
                otherwise
                    turb_ntu = 0.0;
            end

            switch upper(S.mission)
                case "SEARCH"
                    mission_mode = 'DIRECTIVITY';
                case "TRACKING"
                    mission_mode = 'PENETRATION';
                otherwise
                    mission_mode = 'SURVEY';
            end

            env_inputs = struct( ...
                'depth_m', 50.0, ...
                'temperature_c', S.temperature, ...
                'salinity_psu', S.salinity, ...
                'turbidity', turb_ntu, ...
                'noise_penalty_db', 0.0 ...
            );

            [all_metrics, decision] = evaluate_profile_performance(S.range, env_inputs, mission_mode);

            if iscell(all_metrics)
                lowOK  = all_metrics{1}.is_viable;
                balOK  = all_metrics{2}.is_viable;
                highOK = all_metrics{3}.is_viable;
            else
                lowOK  = all_metrics(1).is_viable;
                balOK  = all_metrics(2).is_viable;
                highOK = all_metrics(3).is_viable;
            end

            selected = string(decision.candidate_name);
            confidence = decision.profile_selection_confidence;
        else
            [lowOK, balOK, highOK] = profileViability(S.range, S.temperature, ...
                S.salinity, S.turbidity);

            if lowOK
                selected = "LOW_FREQUENCY";
                confidence = confidenceFor("LOW_FREQUENCY", S.range, S.turbidity);
            elseif balOK
                selected = "BALANCED";
                confidence = confidenceFor("BALANCED", S.range, S.turbidity);
            elseif highOK
                selected = "HIGH_FREQUENCY";
                confidence = confidenceFor("HIGH_FREQUENCY", S.range, S.turbidity);
            else
                selected = "NO_VALID_PROFILE";
                confidence = 0;
            end
        end

        % Update dashboard text
        rangeValue.Text = sprintf('%.0f m', S.range);
        tempValue.Text = sprintf('%.1f °C', S.temperature);
        salValue.Text = sprintf('%.1f PSU', S.salinity);
        turbValue.Text = char(S.turbidity);

        lowValue.Text = viabilityText(lowOK);
        balancedValue.Text = viabilityText(balOK);
        highValue.Text = viabilityText(highOK);

        setViabilityColor(lowValue, lowOK);
        setViabilityColor(balancedValue, balOK);
        setViabilityColor(highValue, highOK);

        missionValue.Text = char(S.mission);
        selectedValue.Text = char(selected);
        confidenceValue.Text = sprintf('%.2f', confidence);

        if selected == "NO_VALID_PROFILE"
            statusValue.Text = 'NO PROFILE AVAILABLE';
            statusValue.FontColor = [0.75 0.1 0.1];
            profileLamp.Color = [0.8 0.1 0.1];
        else
            statusValue.Text = 'PROFILE READY FOR NEXT PING';
            statusValue.FontColor = [0.1 0.5 0.1];
            profileLamp.Color = [0.2 0.7 0.2];
        end

        drawnow limitrate
    end

    function [lowOK,balOK,highOK] = profileViability(range,temp,sal,turb)
        lowMax = 220;
        balMax = 170;
        highMax = 120;

        penalty = 0;

        if turb == "Moderate"
            penalty = 5;
        elseif turb == "High"
            penalty = 15;
        end

        penalty = penalty + 0.4*abs(temp-20) + 0.2*abs(sal-35);

        lowOK  = range <= (lowMax-penalty);
        balOK  = range <= (balMax-penalty);
        highOK = range <= (highMax-penalty);
    end

    function txt = viabilityText(ok)
        if ok
            txt = 'VIABLE';
        else
            txt = 'NOT VIABLE';
        end
    end

    function setViabilityColor(label,ok)
        if ok
            label.FontColor = [0.1 0.55 0.1];
        else
            label.FontColor = [0.75 0.1 0.1];
        end
    end

    function c = confidenceFor(profile,range,turb)
        switch profile
            case {"LOW", "LOW_FREQUENCY"}
                c = 0.72 + 0.0005*(145-range);
            case "BALANCED"
                c = 0.72 + 0.001*(145-range);
            case {"HIGH", "HIGH_FREQUENCY"}
                c = 0.70 + 0.001*(120-range);
            otherwise
                c = 0;
        end

        if turb == "High"
            c = c - 0.08;
        elseif turb == "Low"
            c = c + 0.04;
        end

        c = max(0,min(0.99,c));
    end
end

