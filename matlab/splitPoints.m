function obj = splitPoints(obj)
% called for a split points experiment. Will return a split points object
% appended to umbrealla points object with splitPercent number of cells 

splitPercent = obj.inputParameters.splitPercent;

total_points = numel(obj.all_points.X);

% the number of points to keep
n_keep = round(total_points * (splitPercent/100));
q = splitPercent;


points_fields = fieldnames(obj.all_points);

%indexs of random points to keep
keep_ind = randsample(1:total_points, n_keep, true);

%build the split points field of the new p_obj, populated by subsets of
%points
for i = 1:numel(points_fields)
    
    f_name = points_fields{i};
    val = obj.all_points.(f_name);
    
    if length(val) == total_points
        obj.split_points.(f_name) = val(keep_ind);
    end
end

%Run the split points object through functions to recalculate their
%grouping and centroids and add this info to the structure

obj.split_points = ParseForMaskMaker(obj.split_points, obj.inputParameters);

n_groups = max(obj.split_points.Group);

PhaseMasks = cell(n_groups,1);
TransformedSLMTargets = cell(n_groups,1);

for i = 1:obj.split_points.numGroups
    PhaseMasks{i} = zeros(521,512);
    TransformedSLMTargets{i} = ones(512,512);
end
obj.split_points.q = q;
obj.split_points.PhaseMasks = PhaseMasks;
obj.split_points.TransformedSLMTargets = TransformedSLMTargets;