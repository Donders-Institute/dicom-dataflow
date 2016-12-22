STREAMER_URL = 'http://pacs.dccn.nl:3001'

function submitStreamerJob(seriesId)
    -- submit a stager job to upload series data to RDM 
    local http = require('socket.http')
    local ltn12 = require('ltn12')
    local mime = require('mime')

    local response_body = {} 
    local res, code, response_header, status = http.request {
        url = STREAMER_URL .. '/mri/series/' .. seriesId,
        method = 'POST',
        headers = {
            ["Authorization"]  = "Basic " .. (mime.b64("admin:admin"))
        },
        sink = ltn12.sink.table(response_body)
    }

    if code == 200 then
        local msg = ParseJson(table.concat(response_body)) ['message']
        print('streamer job submitted: ' .. msg)
        return true
    else
        print('Oops! streamer return: ' .. code)
        return nil
    end
end

function OnStableSeries(seriesId, tags, metadata)
    -- hand it over to the streamer
    print('submitting streamer job for stable series ' .. seriesId)
    local ick = submitStreamerJob(seriesId)
end
