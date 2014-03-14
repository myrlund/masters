class Classification < ActiveRecord::Base
  belongs_to :cluster
  has_many :feature_values

  def data
    Hash[feature_values.map {|fv| [fv.feature, fv.value] }].symbolize_keys
  end
end
