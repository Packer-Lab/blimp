function obj = PointsProcessor(points_path, varargin)
%takes an input of a naparm Points object and returns a points object that can be parsed to
%phase mask and gpl makers
% JR 2019. Meat by LR 2018
warning off;

p = inputParser;
p.addParameter('onlyGroupWithinPlane', true);
p.addParameter('GroupSize', 'all');

%whether to make phase masks for all points based on GroupSize etc
p.addParameter('processAll', false);

%whether to run a splitpoints experiment
p.addParameter('splitPoints',false);
p.addParameter('splitPercent', []);

p.addParameter('Save', false);
p.addParameter('SavePath', []);

parse(p, varargin{:});

%load the naparam points structure given in points_path
s = load(points_path);
Points = s.points;

% remove group information from the starting Points object. Groups will be
% generated later and saving these + the initial groups from naparm is
% confusing
Points = rmfield(Points, {'Group', 'GroupCentroidX', 'GroupCentroidY'});

%init processed points object
obj = {};
obj.all_points = Points;
obj.inputParameters = p.Results;


if obj.inputParameters.processAll
    
    %build phase massks from all the points
    obj = processAllPoints(obj);
    
end

if obj.inputParameters.splitPoints
    
    if isempty(obj.inputParameters.splitPercent)
        error('need to provide percentage to keep if splitting points')
    end
     
    obj = splitPoints(obj);
    
end

  
%
% [PhaseMasks, TransformedSLMTargets] = SLMPhaseMaskMakerCUDA3D_v2(...
%             'Points', p_obj.split_points.points_array,...
%             'all_Galvo_Positions', p_obj.split_points.galvo_positions,...
%             'Save', false,...
%             'Do3DTransform', true);

