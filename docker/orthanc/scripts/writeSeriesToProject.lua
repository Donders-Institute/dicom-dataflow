TARGET_PRJ = '/project'
ADMINS = 'h.lee@dccn.nl,mp.zwiers@gmail.com'
STAGER_URL = 'http://stager.dccn.nl:3000'
STAGER_USER = 'root'
RDM_USER = 'irods'

function ToAscii(s)
    -- http://www.lua.org/manual/5.1/manual.html#pdf-string.gsub
    return s:gsub('[^a-zA-Z0-9-/ ]', '_')
end

function sendAlert(m)
    -- send alert email to administrators
    local mail = io.popen("mail -s '!!PACS alert!!' " .. ADMINS, "w")
    mail:write("" .. m .. "\n")
    mail:close()
    return true
end

function DirExists(strFolderName)
    -- what a creative way to check whether the directory exists, LUA sucks!!
    local f = io.popen("if [ -d " .. strFolderName .. " ]; then echo 1; else echo 0; fi", 'r')
    local o = f:read("*a")
    f:close()
    
    if string.match(o, '^1.-') then
       print("directory " .. strFolderName .. " exists") 
       return true
    else
       print("directory " .. strFolderName .. " does not exists")
       return false
    end
end

function getDacForProject(projectId)

    -- get DAC namespace for a project
    local http = require('socket.http')
    local ltn12 = require('ltn12')
    local mime = require('mime')

    local response_body = {} 

    local res, code, response_header, status = http.request {
        url = STAGER_URL .. '/rdm/DAC/project/' .. projectId,
        method = 'GET',
        headers = {
            ["Authorization"]  = "Basic " .. (mime.b64("admin:admin")),
            ["Content-Type"]   = "application/json",
        },
        sink = ltn12.sink.table(response_body)
    }

    if code == 200 then
        local collName = ParseJson(table.concat(response_body)) ['collName']
        print('DAC for ' .. projectId .. ': ' .. collName)
        return collName
    else
        print('DAC for ' .. projectId .. ': unknown')
        return nil
    end
end

function submitStagerJob(seriesId, srcURL, dstURL)
    -- submit a stager job to upload series data to RDM 
    local http = require('socket.http')
    local ltn12 = require('ltn12')
    local mime = require('mime')

    local stagerJob = {}
    stagerJob["type"] = "rdm" 
    stagerJob["data"] = {}
    stagerJob["options"] = {}
    stagerJob["data"]["clientIF"] = 'irods'
    stagerJob["data"]["stagerUser"] = STAGER_USER
    stagerJob["data"]["rdmUser"] = RDM_USER
    stagerJob["data"]["srcURL"] = srcURL .. '/'
    stagerJob["data"]["dstURL"] = dstURL .. '/'
    stagerJob["data"]["title"] = '[' .. os.date("!%c") .. '] Orthanc series: ' .. seriesId
    stagerJob["data"]["timeout"] = 3600
    stagerJob["data"]["timeout_noprogress"] = 600
    stagerJob["options"]["attempts"] = 5
    stagerJob["options"]["backoff"] = {}
    stagerJob["options"]["backoff"]["delay"] = 60000
    stagerJob["options"]["backoff"]["type"] = "fixed"

    local request_body = DumpJson(stagerJob)
    local response_body = {} 

    local res, code, response_header, status = http.request {
        url = STAGER_URL .. '/job',
        method = 'POST',
        headers = {
            ["Authorization"]  = "Basic " .. (mime.b64("admin:admin")),
            ["Content-Type"]   = "application/json",
            ["Content-Length"] = request_body:len()
        },
        source = ltn12.source.string(request_body),
        sink = ltn12.sink.table(response_body)
    }

    if code == 200 then
        local jid = ParseJson(table.concat(response_body)) ['id']
        print('stager job ' .. jid .. ' submitted')
        return jid 
    else
        print('Oops! stager return: ' .. code)
        return nil
    end
end

function OnStableSeries(seriesId, tags, metadata)

    local instances = ParseJson(RestApiGet('/series/' .. seriesId)) ['Instances']
    local patient = ParseJson(RestApiGet('/series/' .. seriesId .. '/patient')) ['MainDicomTags']
    local study = ParseJson(RestApiGet('/series/' .. seriesId .. '/study')) ['MainDicomTags']
    local series = ParseJson(RestApiGet('/series/' .. seriesId)) ['MainDicomTags']
    -- parse PatientName to get project id
    local t = {}
    local j = 1
    for pp in string.gmatch(patient['PatientID'], "([^_]+)") do
        t[j] = pp
        j = j + 1
    end

    -- project storage directory
    local projectDir = TARGET_PRJ .. '/' .. t[1]

    print('Writing stable series ' .. seriesId .. ' to project: ' .. t[1])
 
    if DirExists(projectDir) then
 
       -- compose path to path of the image instance
       local path = projectDir .. '/raw/' ..
                    t[2] .. '/' ..
                    study['StudyID'] .. '/' ..
                    string.format("%03d", series['SeriesNumber']) .. '-' .. ToAscii(series['SeriesDescription'])
 
       for i, instance in pairs(instances) do
       
          local tags = ParseJson(RestApiGet('/instances/' .. instance)) ['MainDicomTags']
  
          -- Retrieve the DICOM file from Orthanc
          local dicom = RestApiGet('/instances/' .. instance .. '/file')
  
          -- Create the subdirectory (CAUTION: For Linux demo only, this is insecure!)
          -- http://stackoverflow.com/a/16029744/881731
          os.execute('mkdir -p "' .. path .. '"')

          -- Compose absolute file name 
          local fname = path .. '/' .. string.format("%05d", tags['InstanceNumber']) .. '_' .. tags['SOPInstanceUID'] .. '.IMA'
  
          -- Write to the file
          local target = io.open(fname, 'wb')

          if not target then
              -- Sending error message to PACS manager
              -- sendAlert("cannot write data to project: " .. projectDir .. "\n\nfile: " .. fname)

              -- throw out an error to interrupt the for-loop
              error("cannot write data file: " .. path)
          else
              target:write(dicom)
              target:close()
          end
       end
 
       -- Submit job to stage series to RDM
       -- get DAC namespace from the stager
       local projectDirRdm = getDacForProject(t[1])
       if projectDirRdm then
           local path_rdm = 'irods:' .. projectDirRdm .. '/raw/' ..
                            t[2] .. '/' ..
                            study['StudyID'] .. '/' ..
                            string.format("%03d", series['SeriesNumber']) .. '-' .. ToAscii(series['SeriesDescription'])
        
           print('submitting stager job for series ' .. seriesId)
           local ick = submitStagerJob(seriesId, path, path_rdm)
           if not ick then
               -- Sending error message to PACS manager
               -- sendAlert("fail sending RDM staging job: " .. path)
        
               -- throw out an error to interrupt the for-loop
               error("fail sending RDM staging job: " .. path)
           end
        else
           print("No DAC defined for project: " .. t[1] .. ', RDM archive skipped.')
        end
    else
        print('project directory ' .. projectDir .. ' not exist, skipped.')
    end
end
