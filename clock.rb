require 'clockwork'
require 'stalker'
include Clockwork

handler do |job|
  Stalker.enqueue(job)
end

every 1.minutes, 'lemme-check-that'
