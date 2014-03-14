class Cluster < ActiveRecord::Base
  belongs_to :run
  has_many :classifications
  has_many :cluster_statistics, :class_name => "ClusterStatistics"

  # The features and the center values are assumed to be in the same order
  serialize :center

  def features
    run.features
  end

  def pretty_center
    Hash[features.zip(center)]
  end

  def size
    classifications.count
  end

  def statistics
    feature_hashes = features.map {|f| feature_statistics(f) }

    Hash[features.zip(feature_hashes)]
  end

  def feature_statistics(feature)
    begin
      cluster_statistics.find_by!(feature: feature).to_hash

    rescue ActiveRecord::RecordNotFound
      require 'descriptive_statistics/safe'
      feature_values = values_for_feature(feature)
      generated_statistics = feature_values.extend(DescriptiveStatistics).descriptive_statistics

      cluster_statistics.create(generated_statistics.merge(feature: feature)).to_hash
    end
  end

  protected

  def values_for_feature(feature)
    # Grab FeatureValue matching feature for each classification
    classifications.includes(:feature_values)
                   .map {|c| c.feature_values.select {|fv| fv.feature == feature }.first }
                   .select(&:present?) # Filter out any nil values
                   .map(&:value)       # Get their values
  end
end
