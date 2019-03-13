function obj = processAllPoints(obj)

obj.all_points = ParseForMaskMaker(obj.all_points, obj.inputParameters);
%obj.all_points = ParseForMarkpoints(obj.all_points, obj.inputParameters);
numGroups = obj.all_points.numGroups;
SaveNames = cell(numGroups,1);
for i = 1:numGroups
    SaveNames{i} = ['allGroups_mask_' num2str(i) '_.tiff' ];
end
keyboard


% [PhaseMasks, TransformedSLMTargets] = SLMPhaseMaskMakerCUDA3D_v2(... 
%             'Points', obj.all_points.points_array,...
%             'all_Galvo_Positions', obj.all_points.galvo_positions,... 
%             'Save', true,...
%             'SaveDirectory',obj.inputParameters.SavePath,...
%             'SaveName', SaveNames,...
%             'Do3DTransform', false,...
%             'AutoAdjustWeights', false);
        
[PhaseMasks, TransformedSLMTargets] = SLMphaseMakerJR('Points', obj.all_points.points_array, 'SaveDirectory', obj.inputParameters.SavePath,...
                                                      'SaveName', SaveNames);

obj.all_points.PhaseMasks = PhaseMasks;
obj.all_points.TransformedSLMTargets = TransformedSLMTargets;

