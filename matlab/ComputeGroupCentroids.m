function Points = ComputeGroupCentroids(Points)
% calculate group centroids and offset targets
% JR 2019, meat by LR 2018

numPoints = numel(Points.X);

Group = Points.Group;
numGroups = max(Group);

offset_x = zeros(numPoints,1);
offset_y = zeros(numPoints, 1);

centroid_x = zeros(numGroups,1);
centroid_y = zeros(numGroups,1);

for group = 1:numGroups
    
    groupIndices = find(Points.Group==(group));
    
    x = Points.X(groupIndices)';
    y = Points.Y(groupIndices)';
    groupPoints = [x y];
    
    [OffsetPoints, GroupCentroid] = ZOBlockAvoider(groupPoints);
    
    offset_x(groupIndices) = OffsetPoints(:,1);
    offset_y(groupIndices) = OffsetPoints(:,2);
    centroid_x(group) = GroupCentroid(1);
    centroid_y(group) = GroupCentroid(2);
    
end

Points.offset_x = offset_x;
Points.offset_y = offset_y;

Points.centroid_x = centroid_x;
Points.centroid_y = centroid_y;






