function obj = processAllPoints(obj)

obj.all_points = ParseForMaskMaker(obj.all_points, obj.inputParameters);
obj.all_points = ParseForMarkpoints(obj.all_points, obj.inputParameters);
numGroups = obj.all_points.numGroups;

PhaseMasks = cell(numGroups, 1);
TransformedSLMTargets = cell(numGroups, 1);

%placeholder, remove
for i = 1:obj.all_points.numGroups
    PhaseMasks{i} = zeros(521,512);
    TransformedSLMTargets{i} = ones(512,512);
end

obj.all_points.PhaseMasks = PhaseMasks;
obj.all_points.TransformedSLMTargets = TransformedSLMTargets;

