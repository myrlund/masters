class CreateClassifications < ActiveRecord::Migration
  def change
    create_table :classifications do |t|
      t.string :person
      t.references :cluster, index: true

      t.timestamps
    end
  end
end
