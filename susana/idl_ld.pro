
;;old one
;get limb darkening coeficients automaticly
  teff=5400.
  logg=4.5
  metal=0.0

;;wsp103
  teff=6110.
  logg = 4.22
  metal = 0.06 
;;filters   0=u,1=v,2=b,3=y,4=U,5=B,6=V,7=R,8=I,9=J,10=H,11=K 
  
;; ;;quadratic limb darkening from idl
  transit, c1, c2,  b1=6 , teff=teff, lg1=logg, mh1=metal



;;; From exofast

 ;;; bands = ['U','B','V','R','I','J','H','K',$
 ;;;        'Sloanu','Sloang','Sloanr','Sloani','Sloanz',$
 ;;;        'Kepler','CoRoT','Spit36','Spit45','Spit58','Spit80',$
  ;;;       'u','b','v','y']

;;;model  Choose ATLAS or PHOENIX (default ATLAS).
 ;;;    METHOD -  Choose L or F (default L)
;;;;    VT     - The microturbulent velocity (0,2,4,or 8, default 2)
  
;; linld( logg, teff, feh, band, model=model, method=method, vt=vt)
  
  ;;ld= linld( logg, teff, metal,'V')
  ;ld= quadld( logg, teff, metal,'V')
   ld= quadld( logg, teff, metal,'Kepler')
  ;;ld= nonlinld( logg, teff, metal,'V')
  print, ld

  
;;; the new lower one is based on the claret 2011 and it is much better
end
