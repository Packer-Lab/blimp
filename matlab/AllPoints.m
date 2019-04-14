function obj = AllPoints(obj)

% function to process matlab stuff for AllPoints blimp experiment

obj.all_points = ParseForMaskMaker(obj.all_points, obj.inputParameters);

numGroups = obj.all_points.numGroups;
SaveNames = cell(numGroups,1);
for i = 1:numGroups
    SaveNames{i} = ['allGroups_mask_' num2str(i) '_.tiff' ];
end
        
[PhaseMasks, TransformedSLMTargets] = SLMphaseMakerBlimp('Points', obj.all_points.points_array, 'SaveDirectory', obj.inputParameters.SavePath,...
                                                      'SaveName', SaveNames);

obj.all_points.PhaseMasks = PhaseMasks;
obj.all_points.TransformedSLMTargets = TransformedSLMTargets;





