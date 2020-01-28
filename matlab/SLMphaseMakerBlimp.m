function [PhaseMasks, TransformedSLMTargets] = SLMphaseMakerBlimp(varargin)

% Blimp specific SLMPhaseMaskMaker dont use this for naparm
% function can be passed the path to a tif file or a Points list from
% Naparm

save_files = 0;

for v = 1:numel(varargin)
    if strcmpi(varargin{v}, 'tif_file')
        tif_file = varargin{v+1};
    elseif strcmpi(varargin{v},'Points')
        Points = varargin{v+1};
    elseif strcmpi(varargin{v}, 'SaveDirectory')
        saveDirectory = varargin{v+1};
        save_files = 1;
    elseif strcmpi(varargin{v}, 'SaveName')
        SaveNames = varargin{v+1};
    end
end

if exist('tif_file', 'var') && exist('Points', 'var')
    error('this function should not be passed a tif_file and a points list')
end

%MAKE THIS READ THE YML
% Load previously calibrated transform
% improve on this hardcoded path when switch to naparm3
disp('using blimp phase mask maker with hardcoded naparm 2 yaml path')
yaml = ReadYaml("C:\Users\User\Documents\Code\Naparm2\Settings\settings.yml");



% see if AutoAdjustWeights passed as input, if not take value from yaml file
AutoAdjustWeights = yaml.AutoAdjustWeights;
if AutoAdjustWeights
    load(yaml.WeightingFile, 'W');  % loads 'W'
end
SteepnessFudgeFactor = yaml.SteepnessFudgeFactor;
% Find target coordinates



transform_file = yaml.TransformFile;
load(transform_file);



transformChoice = 'Yes';




%create naparm style Points from a tif_file argument
%currently only support a single group of points
if exist('tif_file', 'var')
    
    raw = importdata(tif_file);
    
    [rows,cols] = find(raw == 255);
    
    Points = {};
    
    point_mat = [];
    for i = 1:length(rows)
        point_mat(i,:) = horzcat(cols(i), rows(i), 1, 255);
    end
    
    Points{1} = point_mat;
    
end

%%%% THIS IS THE ORIGINAL SCALING IN HERE THAT I DONT THINK WORKS

% %RL 2018-11-15 for scaling targets according to optical zoom
% % keyboard
% for i = 1:length(Points)
%     for j = 1:size(Points{i},1)
%         for k = 1:2
%             a = Points{i}(j,k); %SLM target position
%             b = abs(255-a); %Distance between SLM target and galvo
%             c = (b*2)/FOVsize_OpticalZoom; %scale the distance from a 2x zoom transform
%             if Points{i}(j,k) < 255
%                 Points{i}(j,k) = 255-c;
%             else
%                 Points{i}(j,k) = 255+c;
%             end
%         end
%     end
% end


%%% RESCALING TAKEN FROM SLMphaseMakerJR.m
%RL 2018-11-15 for scaling targets according to optical zoom
FOVsize_OpticalZoom = yaml.FOVsize_OpticalZoom;
for i = 1:length(Points)
    for j = 1:size(Points{i},1)
        for k = 1:2
            a = Points{i}(j,k); %SLM target position
            b = abs(255-a); %Distance between SLM target and galvo
            c = b/FOVsize_OpticalZoom; %scale the distance from a 2x zoom transform
            if Points{i}(j,k) < 255
                Points{i}(j,k) = 255-c;
            else
                Points{i}(j,k) = 255+c;
            end
        end
    end
end

% keyboard
x_offset =  yaml.TForm_X_offset;
y_offset =  yaml.TForm_Y_offset;

%add the offset from the yaml
for i = 1:length(Points)
    P = Points{i};
    P(:,1) = P(:,1) + x_offset;
    P(:,2) = P(:,2) + y_offset;
    Points{i} = P;
end

TransformedSLMTargets = {};
PhaseMasks = {};

NumGroups = numel(Points);


for idx = 1:NumGroups
    
    if (idx<100)&(idx>=10); buffer = '0'; elseif idx>100; buffer = ''; else buffer = '00'; end
    group_str = ['group' buffer num2str(idx) '_'];
    num_targets = numel(Points{idx}(:,1));
    num_planes = ceil(range(unique(Points{idx}(:,3)))+1);
    
    InputTargets = zeros(512,512,num_planes);
    for i = 1:num_targets
        row = round(Points{idx}(i,2));
        col = round(Points{idx}(i,1));
        slice = round(Points{idx}(i,3) - min(Points{idx}(:,3)) + 1);
        val = Points{idx}(i,4);

        InputTargets(row,col,slice) = val;
            
    end
    
    FocalSlice = -min(Points{idx}(:,3)) + 1;
    
    [y,x,~] = find(InputTargets);
    
    % Convert target *coordinates* directly from 2P to SLM space
    switch transformChoice
        case 'Yes'
            [u,v] = transformPointsForward(tform,x,y);
            u     = round(u);
            v     = round(v);
        case 'No'
            u = x; v = y;
    end
    
    % Build transformed targets image
    SLMtargets = uint8(zeros(512,512));
    for i = 1:length(u)
        SLMtargets(v(i),u(i)) = 255;
    end
    
    
    %figure, imshow(SLMtargets)
    
    if save_files
        
        transformed_dir = [saveDirectory filesep 'PhaseMasks' filesep 'TransformedTargets' filesep];
        
        if  ~exist(transformed_dir, 'dir')
            mkdir(transformed_dir)
        end
        
        imwrite(SLMtargets, [transformed_dir group_str 'Transformed.tif']);
    end
    
    % Weight the target pixel intensity by distance from zero order
    %     slope                = 75/183;
    %     b                    = 25;
    %     DistFromZeroOrderIdx = 1:0.1:183;
    %     WeightByDist         = slope*DistFromZeroOrderIdx + b;
    %     WeightByDist         = WeightByDist/100;
    %     for i = 1:length(u)
    %         d(i) = sqrt((u(i)-256)^2 + (v(i)-256)^2);
    %     end
    %     for i = 1:length(u)
    %         ThisDistIdx = find(d(i)<DistFromZeroOrderIdx,1,'first');
    %         ThisDistIdx(d(i)>max(DistFromZeroOrderIdx)) = length(DistFromZeroOrderIdx); %added 20141129
    %         p(i) = 255*WeightByDist(ThisDistIdx);
    %     end
    %
    %    Build final transformed, weighted targets image
    %
    %     if strcmp(weightMe, 'Yes')
    %         SLMtargets = uint8(zeros(512,512));
    %         for i = 1:length(u)
    %             SLMtargets(v(i),u(i)) = p(i);
    %         end
    %     end
    
    
    if AutoAdjustWeights
        distances = pairwiseDistance([u v], [256 256]);
        % fudge weights steepness (slope of fit)
        W.p_edited = W.p;
        W.p_edited(1) = W.p_edited(1) * SteepnessFudgeFactor;
        
        % estimate intensites of spots based on calibration data
        estimatedIntensity = polyval(W.p_edited, distances);
        MAX = polyval(W.p, 0);
        normEstimatedIntensity = estimatedIntensity / MAX;
        
        % compute weights from estimated intensites
        weights = (1 ./ normEstimatedIntensity);  % subtract to ensure linear correction. division does not.
        
        % apply weights
        I_weighted = val .* weights;
        
        if any(I_weighted<=0)
            disp('ERROR: Some spot weights <= 0')
            I_weighted(I_weighted<=0) = min(I_weighted(I_weighted>0));
        end
        
        % save weights
        val_orig = val;
        val = I_weighted;
    end
    
    
    if save_files
        weighted_dir = [saveDirectory filesep 'PhaseMasks' filesep 'TransformedTargets' filesep];
        if  ~exist(weighted_dir, 'dir')
            mkdir(weighted_dir)
        end
        
        imwrite(SLMtargets, [weighted_dir group_str 'TransformedWeighted.tif']);
    end
    
    TransformedSLMTargets{idx} = SLMtargets;
    
    % Computer generated hologram using the Gerchberg-Saxton algorithm
    % Dr F.A. van Goor, University of Twente. April 2010
    % Reorganized by Adam Packer December 2013
    Nitt    = 10; % number of itererations
    m       = 1;
    nm      = 1e-9*m;
    mm      = 1e-3*m;
    cm      = 1e-2*m;
    lambda  = 1064*nm; %red HeNe laser
    SLMsize = 7.68*mm; %the HoloEye LCD is W x H = 25.4mm x 19.05 mm
    N       = 512; %The HoloEye LCD has W x H = 800 x 600 pixels, we use a square grid
    imageD  = double(SLMtargets); %The LightPipes command 'LPSubIntensity' requires an array of doubles as input
    UniformIntensity = ones(N); % We need a matrix filled with 1's to substitute a uniform intensity profile
    
    % The iteration loop to get the phase distribution
    F = LPBegin(SLMsize,lambda,N); % We start with a plane wave distribution with amplitude 1 and phase 0
    for i = 1:Nitt
        F = LPPipFFT(1,F); %Take the 2-D Fourier transform of the field
        F = LPSubIntensity(imageD,F); % Substitute the original intensity distribution, leave the phase unchanged
        F = LPPipFFT(-1,F); % Take the inverse Fourier transform
        F = LPSubIntensity(UniformIntensity,F); % Substitute a uniform intensity, leave the phase unchanged
        fprintf('%s ','.'); % monitor the number of iterations done in the command window
    end
    fprintf('\n');
    
    Phase       = LPPhase(F); %Extract the phase distribution from the field
    PhaseZeroed = Phase+abs(min(min(Phase)));
    
    % Convert
    Phase8      = PhaseZeroed*(255/max(max(PhaseZeroed)));
    phaseMask8  = uint8(Phase8);
    %     Phase16     = PhaseZeroed*(65535/max(max(PhaseZeroed)));
    %     phaseMask16 = uint16(Phase16);
    PhaseMasks{idx} = phaseMask8;
    % Save
    if save_files
        phase_dir = [saveDirectory filesep 'PhaseMasks' filesep];
        if ~exist(phase_dir, 'dir')
            mkdir(phase_dir);
        end
        imwrite(phaseMask8, [phase_dir  group_str 'phaseMask.tif']);
    end
    
end


