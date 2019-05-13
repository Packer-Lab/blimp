function obj = splitPoints(obj)
% called for a split points experiment. Will return a split points object
% appended to umbrealla points object with splitPercent number of cells 

total_points = numel(obj.all_points.X);

%indexs of random points to keep
keep_idx = SelectSubsetPoints(obj);

points_fields = fieldnames(obj.all_points);

%build the split points field of the new p_obj, populated by subsets of
%points
for i = 1:numel(points_fields)
    
    f_name = points_fields{i};
    val = obj.all_points.(f_name);
    
    if length(val) == total_points
        obj.split_points.(f_name) = val(keep_idx);
    end
end

%Run the split points object through functions to recalculate their
%grouping and centroids and add this info to the structure
obj.split_points = ParseForMaskMaker(obj.split_points, obj.inputParameters);

saveName = ['splitPoints_mask_subsetSize' num2str(obj.inputParameters.subsetSize) '.tiff'];

[PhaseMasks, TransformedSLMTargets] = SLMphaseMakerBlimp('Points', obj.split_points.points_array, 'SaveDirectory', obj.inputParameters.SavePath,...
                                                         'SaveName', saveName);
                                                 
obj.split_points.PhaseMasks = PhaseMasks;
obj.split_points.TransformedSLMTargets = TransformedSLMTargets;


% useful debugging tool to plot points 
% fig = zeros(512,512);
% for i = 1:length(obj.split_points.X)
%     fig(obj.split_points.X(i), obj.split_points.Y(i)) = 1;
% end
% figure
% imshow(fig)

