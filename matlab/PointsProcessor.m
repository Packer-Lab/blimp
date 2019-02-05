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

s = load(p.Results.PointsPath);
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

%save placeholder, remove
if ~isempty(obj.inputParameters.SavePath)
    save(obj.inputParameters.SavePath, 'obj');
end






