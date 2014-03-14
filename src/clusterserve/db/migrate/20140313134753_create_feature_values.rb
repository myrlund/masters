class CreateFeatureValues < ActiveRecord::Migration
  def change
    create_table :feature_values do |t|
      t.references :classification, index: true
      t.string :feature, index: true
      t.decimal :value

      t.timestamps
    end
    add_index :feature_values, :feature
  end
end
