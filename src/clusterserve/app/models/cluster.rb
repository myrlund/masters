class Cluster < ActiveRecord::Base
  belongs_to :run
  has_many :classifications
  has_many :cluster_statistics, :class_name => "ClusterStatistics"

  def self.n_largest(n)
    ids = select('clusters.id, count(classifications.id) AS classification_count').
          joins(:classifications).
          group('clusters.id').
          order('classification_count DESC').
          limit(n).map {|obj| obj.id }

    where(id: ids)
  end

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
    stats = features.map {|f| feature_statistics(f) }

    Hash[features.zip(stats)]
  end

  def feature_statistics(feature)
    begin
      stats = cluster_statistics.find_by!(feature: feature)
    rescue ActiveRecord::RecordNotFound
      require 'descriptive_statistics/safe'
      feature_values = values_for_feature(feature)
      generated_statistics = feature_values.extend(DescriptiveStatistics).descriptive_statistics

      puts "Generated statistics for #{feature}."

      stats = cluster_statistics.create(generated_statistics.merge(feature: feature))
    end

    stats
  end

  protected

  def values_for_feature(feature)
    # Grab FeatureValue matching feature for each classification
    classifications.includes(:feature_values)
                   .map {|c| c.feature_values.select {|fv| fv.feature == feature }.first }
                   .select(&:present?) # Filter out any nil values
                   .map(&:value)       # Get their values
  end

  def serializable_hash(options={})
    super(options.merge({methods: [:size]}))
  end
end
