require 'descriptive_statistics/safe'
class StatisticsWorker
  include Sidekiq::Worker

  def perform(stats_id)
    stats = ClusterStatistics.find(stats_id)
    feature = stats.feature
    cluster = stats.cluster

    feature_values = cluster.values_for_feature(feature)

    generated_statistics = feature_values.extend(DescriptiveStatistics).descriptive_statistics

    puts "Generated statistics for #{feature}: #{generated_statistics.to_s}"

    stats.update_attributes(generated_statistics)
  end
end