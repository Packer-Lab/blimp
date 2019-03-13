function obj = PointsProcessor(naparm_path, varargin)
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

points_path = dir(fullfile(naparm_path, '*Points.mat'));
gpl_path = dir(fullfile(naparm_path, '*.gpl'));

p.addParameter('PointsPath', strcat(points_path.folder, '/', points_path.name));
p.addParameter('GPLpath', strcat(gpl_path.folder, '/', gpl_path.name));
parse(p, varargin{:});


%load the naparam points structure given in points_path

naparm = load(p.Results.PointsPath);
naparm_points = naparm.points;
% remove group information from the starting Points object. Groups will be
% generated later and saving these + the initial groups from naparm is
% confusing
%Points = rmfield(Points, {'Group', 'GroupCentroidX', 'GroupCentroidY'});

Points.X = naparm_points.X;
Points.Y = naparm_points.Y;
%add plane information to structures from naparm2
if ~isfield(Points, 'Z')
    Points.Z = ones(1, length(Points.X));
end


%init processed points object
obj = {};
obj.all_points = Points;
obj.inputParameters = p.Results;


if obj.inputParameters.processAll
    
    %build phase masks from all the points
    obj = processAllPoints(obj);
    
end

if obj.inputParameters.splitPoints
    
    if isempty(obj.inputParameters.splitPercent)
        error('need to provide percentage to keep if splitting points')
    end
    
    obj = splitPoints(obj);
    
end

%save placeholder, remove
if ~isempty(obj.inputParameters.SavePath)
    save(obj.inputParameters.SavePath, 'obj');
end






