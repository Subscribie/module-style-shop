from flask import (Blueprint)
from subscribie.db import get_jamla

module_style_shop = Blueprint('style_shop', __name__, template_folder='templates')

@module_style_shop.app_context_processor
def inject_custom_style():
  # Work out custom styling from jamla entry. 
	# Custom styling is applied by adding a "options->stlyes" entry
	# under the theme declaration.
	# Style entered will be injected into the base of the template
	# output as inline css using <style> tags.
	# 
  # Example valid entry:
	#
  # theme:
  # name: jesmond
  # options: 
  #   styles:
  #     - selector: body
  #       rules: 
  #         - color: red
  #         - background: orange
	#			- selector: .kcBlue
	#				rules:
	#					- background: black
	#					- border: 5px solid yellow;

  jamla = get_jamla()
  declarations = ''
  for style in jamla['theme']['options']['styles']:
    selector = style['selector']
    for propertyValues in style['rules']:
      for cssProperty in propertyValues:
        declaration = "{cssProperty}: {propertyValue};".format(cssProperty=cssProperty, propertyValue=propertyValues[cssProperty])
      declarations += declaration

  # Wrap declarations with selector
  ruleSet = "{selector}{declarations}".format(selector=selector, declarations='{'+declarations+'}')
  # Wrap style tags
  custom_css = ''.join(['<style type="text/css">', ruleSet, '</style>'])
  return dict(custom_css=custom_css)
