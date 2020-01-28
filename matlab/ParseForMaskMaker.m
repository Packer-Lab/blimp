function Points = ParseForMaskMaker(Points, inputParameters)
% function to parse attributes of Points object to format required by SLMPhaseMaskMakerCUDA3D_v2
% also calculates offset points and centroids to avoid zob

Points = GroupPoints(Points, inputParameters);
Points = ComputeGroupCentroids_JR(Points);

%points array in the form required by SLMPhaseMaskMaker
%offset targets used to avoid zob

Points.galvo_positions = horzcat(Points.centroid_x, Points.centroid_y);

Group = Points.Group;
numGroups = max(Group);

points_array = cell(numGroups,1);

for i = 1:numGroups
    
    %index of each group 
    idx = find(Points.Group==(i));
    points_array{i} = horzcat(Points.offset_x(idx), Points.offset_y(idx), Points.Z(idx)', ones(length(Points.offset_x(idx)),1));
    %points_array{i} = horzcat(Points.X(idx)', Points.Y(idx)', Points.Z(idx)', ones(length(Points.offset_x(idx)),1));
end

Points.numGroups = numGroups;
Points.points_array = points_array;