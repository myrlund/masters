json.array!(@runs) do |run|
  json.extract! run, :id, :algorithm, :params, :comment
  json.url run_url(run, format: :json)
end
