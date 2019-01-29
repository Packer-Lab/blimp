function Points = ComputeGroupCentroids(Points, inputParameters)
% calculate group centroids and offset targets
% JR 2019, meat by LR 2018

Group = Points.Group;

numGroups = max(Group);
groups = unique(Group);


for i = 1:ceil(numGroups)
    groupIndices = find(Points.Group==(i));
    
    x = Points.X(groupIndices)';
    y = Points.Y(groupIndices)';
    groupPoints = [x y];
    [OffsetPoints, GroupCentroid] = ZOBlockAvoider(groupPoints);
    
    Points.OffsetX(groupIndices) = OffsetPoints(:,1);
    Points.OffsetY(groupIndices) = OffsetPoints(:,2);
    Points.GroupCentroidX(groupIndices) = GroupCentroid(1);
    Points.GroupCentroidY(groupIndices) = GroupCentroid(2);
end