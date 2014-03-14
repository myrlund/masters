class CreateClusters < ActiveRecord::Migration
  def change
    create_table :clusters do |t|
      t.references :run, index: true
      t.text       :center
      t.string     :label
      t.decimal    :variance

      t.timestamps
    end
  end
end
