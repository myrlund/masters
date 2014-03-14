class CreateRuns < ActiveRecord::Migration
  def change
    create_table :runs do |t|
      t.string :algorithm
      t.string :params
      t.text   :features
      t.text   :comment

      t.timestamps
    end
  end
end
