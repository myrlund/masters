class FeatureValue < ActiveRecord::Base
  belongs_to :classification

  def feature
    self[:feature].to_sym
  end
end
