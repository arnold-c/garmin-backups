using DataFrames, DataFramesMeta, DelimitedFiles
import HeartRateVariability as HRV

data_path = joinpath(@__DIR__, "elite-hrv/original-files/")

function read_file(file)
    date = file[1:10]
    time = file[12:19]
    time = replace(time, "-" => ":")
    datetime = date * " " * time * " +0000"

    vec = HRV.infile(joinpath(data_path, file))
    data = HRV.time_domain(vec)
    
    DF = DataFrames.DataFrame(pairs(data))
    insertcols!(DF, 1, :timestamp_measurement => datetime) 
    
    return DF
end

function calculate_Rec_Points!(DF)
    @transform!(DF, :Rec_Points = 1.5 .* log.(:rmssd) .+ 2)
    return DF
end


for file in readdir(data_path)
    DF = read_file(file)
    calculate_Rec_Points!(DF)
    print(DF)
end