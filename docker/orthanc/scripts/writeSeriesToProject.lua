function submitStreamerJob(seriesId)
    -- submit a stager job to upload series data to RDM 
    local url = os.getenv('STREAMER_URL') .. '/mri/series/' .. seriesId

    SetHttpCredentials('admin', 'admin')

    local answer = HttpPost(url, nil)
    if answer == nil or answer == '' then
        print('Oops! fail POST to stremaer')
        return nil
    elseif answer == 'ERROR' then
        print('Oops! streamer return: ' .. answer)
        return nil
    else
        print('streamer job submitted: ' .. answer)
        return true
    end
end

function OnStableSeries(seriesId, tags, metadata)
    -- hand it over to the streamer
    print('submitting streamer job for stable series ' .. seriesId)
    local ick = submitStreamerJob(seriesId)
end
