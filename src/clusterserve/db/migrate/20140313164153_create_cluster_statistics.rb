class CreateClusterStatistics < ActiveRecord::Migration
  def change
    create_table :cluster_statistics do |t|
      t.references :cluster, index: true
      t.string :feature
      t.decimal :number
      t.decimal :sum
      t.decimal :variance
      t.decimal :standard_deviation
      t.decimal :min
      t.decimal :max
      t.decimal :mean
      t.decimal :mode
      t.decimal :median
      t.decimal :range
      t.decimal :q1
      t.decimal :q2
      t.decimal :q3

      t.timestamps
    end
  end
end
