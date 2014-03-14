Clusterserve::Application.routes.draw do
  resources :feature_values
  resources :classifications
  resources :runs do
    resources :clusters, shallow: true
  end

  root to: 'runs#index'

end
