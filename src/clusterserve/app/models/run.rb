class Run < ActiveRecord::Base
  has_many :clusters
  has_many :classifications, through: :clusters
  has_many :feature_values, through: :classifications

  default_scope -> { order('created_at DESC') }

  serialize :features

  def params
    JSON.parse(self[:params]).symbolize_keys
  end

  def features
    self[:features].map(&:to_sym)
  end

  def size
    clusters.collect(&:size).sum
  end

  def feature_average(feature)
    feature_index = features.index(feature)
    clusters.collect {|c| c.center[feature_index] * c.size }.sum.to_f / self.size
  end

  def feature_averages
    Hash[features.zip(features.map {|f| feature_average(f) })]
  end

  def timespan_from
    self[:timespan_from] ? Time.at(self[:timespan_from]).to_datetime : nil
  end
  def timespan_to
    self[:timespan_from] ? Time.at(self[:timespan_to]).to_datetime : nil
  end
end
