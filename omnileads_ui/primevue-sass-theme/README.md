
This is how we configure the primevue theme generation and loading.

``` sh
cd omnileads_ui
sass --no-source-map primevue-sass-theme/themes/saga/saga-dark-pink/theme.scss:public/primevue/3.12.0/resources/themes/saga-dark-pink.css

cd public/primevue
ln -s ./3.12.0/resources/themes/saga-dark-pink.css theme.css
```
