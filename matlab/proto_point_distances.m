clear
tic
x_coords = [193,306,245,228,295,329,183,278,241,175,218,241,282,345,326,276,309,334];
y_coords = [133,131,199,281,276,242,165,173,207,226,243,236,193,196,245,286,276,282];
num_points = length(x_coords);

merged = vertcat(x_coords,y_coords);
distances = [];
for i = 1:num_points
    x_point = x_coords(i);
    y_point = y_coords(i);
    
    for ii = 1:num_points
        
        x_measure = x_coords(ii);
        y_measure = y_coords(ii);
        
        distance = pdist([x_point, y_point; x_measure, y_measure]);
        distances(i,ii) = distance;
        
    end
end

%maximum number of pixels apart points can be
max_distance = 111;

distant_idx = find(distances > max_distance);
bool_mat = ones(size(distances));
bool_mat(distant_idx) = 0;

summed = sum(bool_mat, 2);

subsetSize = 10;

%points that have more than subsetSize points close to them
include_idx = find(summed > subsetSize);


%%brute force solution%%
iter = 0;
got_solution = 0;
while 1
    too_far = 0;
    count = 0;
    iter = iter +1;
    if iter > 1000
        disp('couldnt find solution')
        break
    end
    
    rand_point = datasample(include_idx,1);
    close_points = find(bool_mat(rand_point,:));
    %do not include own point
    close_points = close_points(close_points ~= rand_point);
    
    test_selection = datasample(close_points,10, 'Replace', false);
    
    
    for i = 1:length(test_selection)
        x = test_selection(i);
        
        for ii = 1:length(test_selection)
            y = test_selection(ii);
            
            if bool_mat(x,y) == 0
                too_far = 1;
                break
            end
        end
        
        if too_far
            break
        end
  
    end
        
    if too_far
        continue
    else
        disp('got solution yo')
        break
    end
   
end
    
    
    toc
    
fig = zeros(512,512);

for i = 1:length(test_selection)
    point = test_selection(i);
    fig(x_coords(point), y_coords(point)) = 1;
end

imwrite(fig,'result.tiff' )
    
    
    
    
    
    
    
    
    
    
    
    
