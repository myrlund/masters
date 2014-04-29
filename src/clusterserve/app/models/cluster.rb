class Cluster < ActiveRecord::Base
  belongs_to :run
  has_many :classifications
  has_many :feature_values, through: :classifications
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

  def center
    super.map {|n| n.round(3) }
  end

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
      values = values_for_feature(feature)
      mean = values.sum.to_f / values.length
      stats = cluster_statistics.create(feature: feature, mean: mean)
      StatisticsWorker.perform_async(stats.id)
    end

    stats
  end

  def values_for_feature(feature)
    FeatureValue.where(feature: feature, classification_id: classifications.map(&:id)).map(&:value)
  end

  protected

  def serializable_hash(options={})
    super(options.merge(methods: [:size]))
  end
end
