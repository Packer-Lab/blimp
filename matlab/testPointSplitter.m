MEs = {};
gs = [];
ps = [];

group_size = 1:3:100;
percents = [10,20,30,40,50,60,70,80,90,100];
for p = percents
    for g = group_size
        try
            PointsProcessor(naparm_path, 'splitPoints',1,'splitPercent',p,  'GroupSize', g);
        catch ME
            MEs{end+1} = ME;
            gs(end+1) = g;
            ps(end+1) = p;
        end
    end
end

for i = 1:length(MEs)   
    m = MEs{1, i}.message;
    disp(m) 
end