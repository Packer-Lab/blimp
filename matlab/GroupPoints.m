function Points = GroupPoints(Points, inputParameters)
%takes a Points object and returns their group
%JR 2019. meat by LR 2018

onlyGroupWithinPlane = inputParameters.onlyGroupWithinPlane;
GroupSize = inputParameters.GroupSize;


numPoints = numel(Points.X);

if ~strcmp(GroupSize, 'all')
    
    NumGroups = numPoints / GroupSize;
    
    if ceil(NumGroups) ~= floor(NumGroups)
        disp(['This group size would require ' num2str(NumGroups) ' groups']) 
        NumGroups = ceil(NumGroups);
        disp(['Correcting to use ' num2str(NumGroups) ' groups'])     
    end
    
end

% groups points. currently only implements ekmeans grouping
if onlyGroupWithinPlane
    planes = unique(Points.Z);
    numPlanes = numel(planes);
else
    planes = 1;
    numPlanes = 1;
    
    if strcmp(GroupSize,'all')
        GroupSize = numel(Points.X);
    end
end

prevNumGroups = 0;

for i = 1:numPlanes
    
    if onlyGroupWithinPlane
        zIndices = Points.Z == planes(i);
        
        if strcmp(GroupSize, 'all')
            GroupSize = sum(zIndices);
        end
        
        thisNumGroups = sum(zIndices) / GroupSize;
    else
        %i think this is correct (JR) though could cause errors
        zIndices = 1:numPoints;
        thisNumGroups = NumGroups;
    end
    
    data = [Points.Y; Points.X]';
    num_iterations = 150;
    equal = 1;
    [assignments,centroids,varargout] = ekmeans(data(zIndices,:), ceil(thisNumGroups), num_iterations, equal);
    group(zIndices) = assignments' + prevNumGroups;
    prevNumGroups = prevNumGroups + numel(unique(assignments));
    
end


Points.Group = group;


