function obj = Main(naparm_path, varargin)
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
p.addParameter('subsetSize', []);
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

Points.X = naparm_points.X;
Points.Y = naparm_points.Y;

%rescale to 512x512 for compatibility with existing functions
scaling_factor = naparm_points.fovsize_px / 512;
Points.X = round(Points.X / scaling_factor);
Points.Y = round(Points.Y / scaling_factor);




%add plane information to structures from naparm2
if ~isfield(Points, 'Z')
    Points.Z = ones(1, length(Points.X));
end

%init processed points object
obj = {};
obj.all_points = Points;
obj.inputParameters = p.Results;
obj.fovsize_px = naparm_points.fovsize_px;
obj.zoom = naparm_points.zoom;

if obj.inputParameters.processAll
    %build phase masks from all the points
    obj = AllPoints(obj);
end

if obj.inputParameters.splitPoints
    
    if isempty(obj.inputParameters.subsetSize)
        error('need to provide subset sizes to keep if splitting points')
    end
    
    obj = splitPoints(obj);
    
end

%save placeholder, remove
if ~isempty(obj.inputParameters.SavePath)
    save([obj.inputParameters.SavePath filesep 'matlab_input_parameters.mat'], 'obj');
end



