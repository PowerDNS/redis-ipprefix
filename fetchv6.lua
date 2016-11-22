local function log(...)
	redis.call("publish", "log", string.format(...))
end
local key = KEYS[1]
local first = {}
local last = {}
for i,part in ipairs(ARGV) do
	local res = redis.call("ZRANGEBYSCORE", key, part, "inf", "LIMIT", 0, 1, "WITHSCORES")
	if #res == 0 then return end
	log('#res=%s', #res)
	local partialfirst,partiallast=unpack(res)
	log('partialfirst=%s', partialfirst)
	log('part=%s', part)
	if partialfirst > part then return end
	table.insert(first, partialfirst)
	table.insert(last, partiallast)
	key = table.concat(last, '-')
end
first = table.concat(first, '-')
last = table.concat(last, '-')
return {first, last}