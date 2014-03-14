class ClusterStatistics < ActiveRecord::Base
  belongs_to :cluster

  def to_hash
    Hash[self.class.statistics_fields.zip(statistics_values)]
  end

  protected

  def statistics_values
    self.class.statistics_fields.map {|field| send(field) }
  end

  def self.statistics_fields
    [:number, :sum, :variance, :standard_deviation, :min, :max, :mean, :mode, :median, :range, :q1, :q2, :q3]
  end
end
