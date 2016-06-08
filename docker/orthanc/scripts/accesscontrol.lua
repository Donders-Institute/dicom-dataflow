function IncomingHttpRequestFilter(method, uri, ip, username)
   -- Only allow GET requests for non-admin users

  if method == 'GET' then
      return true
   elseif username == 'admin' then
      return true
   else
      return false
   end
end