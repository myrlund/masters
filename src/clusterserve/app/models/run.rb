class Run < ActiveRecord::Base
  has_many :clusters
  serialize :features

  def params
    JSON.parse(self[:params]).symbolize_keys
  end

  def features
    self[:features].map(&:to_sym)
  end
end
