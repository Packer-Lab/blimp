function p_obj = points_processor(points_path, varargin)
%takes an input of a naparm Points object and returns a points object that can be parsed to
%phase mask and gpl makers
% JR 2019. Meat by LR 2018
p = inputParser;
p.addParameter('onlyGroupWithinPlane', true);
p.addParameter('splitPoints',false);
p.addParameter('splitPercent', []);
p.addParameter('GroupSize', 'all');
parse(p, varargin{:});

s = load(points_path);
Points = s.points;

% remove group information from the starting Points object. Groups will be
% generated later and saving these + the initial groups from naparm is
% confusing
Points = rmfield(Points, {'Group', 'GroupCentroidX', 'GroupCentroidY'});

n_points = length(Points.X);

%init processed points object
p_obj = {};
p_obj.allPoints = Points;
p_obj.inputParameters = p.Results;

if p.Results.splitPoints
    
    splitPercent = p.Results.splitPercent;
    
    if isempty(splitPercent)
        error('need to provide percentage to keep if splitting points')
    end
    
    % the number of points to keep
    n_keep = round(n_points * (splitPercent/100));
           
    points_fields = fieldnames(Points);
    
    %indexs of random points to keep
    keep_ind = randsample(1:n_points, n_keep, true);
    
    %build the split points field of the new p_obj, populated by subsets of
    %points
    for i = 1:numel(points_fields)
        f_name = points_fields{i};
        val = Points.(f_name);
        
        if length(val) == n_points
            p_obj.split_points.(f_name) = val(keep_ind);
        end
    end
   
end


%Run the split points object through functions to recalculate their
%grouping and centroids and add this info to the structure
p_obj.split_points =           GroupPoints(p_obj.split_points, p.Results);
p_obj.split_points = ComputeGroupCentroids(p_obj.split_points, p.Results);



