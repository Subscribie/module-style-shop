from flask import (Blueprint, request, render_template, abort, flash, url_for, 
    redirect)
from subscribie.db import get_jamla
from subscribie.auth import login_required
from subscribie import current_app
from jinja2 import TemplateNotFound
import tinycss
import yaml
from flask import Markup

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
  ruleSet = getCustomCSS()
  # Wrap style tags
  if ruleSet is not None:
    custom_css = ''.join(['<style type="text/css">', ruleSet, '</style>'])
    return dict(custom_css=custom_css)
  else:
    return dict()

def getCustomCSS():
  """Return string of any defined custom css rules from Jamla.yaml"""
  jamla = get_jamla()
  if  jamla['theme']['options']['styles'] == []:
    return None # Exit if no custom styles defined

  declarations = ''
  for style in jamla['theme']['options']['styles']:
    selector = style['selector']
    for propertyValues in style['rules']:
      for cssProperty in propertyValues:
        declaration = "{cssProperty}: {propertyValue};".format(cssProperty=cssProperty, propertyValue=propertyValues[cssProperty])
      declarations += declaration

  # Wrap declarations with selector
  ruleSet = "{selector}{declarations}".format(selector=selector, declarations='{'+declarations+'}')
  return ruleSet

@module_style_shop.route('/style_shop/index') # Define a module index page
@module_style_shop.route('/style-shop')
@login_required
def style_shop():
  try:
    # Load custom css rules (if any) and display in an editable textbox
    customCSS = getCustomCSS()
    return render_template('show-custom-css.html', customCSS=customCSS, jamla=get_jamla())
  except TemplateNotFound:
    abort(404)

@module_style_shop.route('/style-shop', methods=['POST'])
@login_required
def save_custom_style():
  jamla = get_jamla()
  # Replace jamla->theme->options->styles with new css rulesets
  jamla['theme']['options']['styles'] = [] # Clear existing styles
  
  css = request.form['css']
  parser = tinycss.make_parser('page3')
  stylesheet = parser.parse_stylesheet(css)
  # Parse each rule, get its rulesets, declarations and save to jamla
  rules = []
  for rule in stylesheet.rules:
    selector = rule.selector.as_css()
    # Add selector to draftJamla
    for declaration in rule.declarations:
      cssProperty = declaration.name
      propertyValue = declaration.value.as_css()
      rules.append({cssProperty:propertyValue})
    jamla['theme']['options']['styles'].append({'selector': selector, 'rules': rules})

  fp = open(current_app.config["JAMLA_PATH"], "w")
  yaml.safe_dump(jamla, fp, default_flow_style=False)
  flash(Markup('Styling updated. View your <a href="/">updated shop</a>'))
    
  return redirect(url_for('style_shop.style_shop'))
