"""Placeholder pages for player comparisons and similarity exploration."""
from flask import Blueprint, render_template

explore_pages = Blueprint('explore', __name__)


@explore_pages.get('/compare')
def compare():
    return render_template('wip.html', title='Compare',
                           description='Compare two players side by side.')


@explore_pages.get('/similarity-map')
def similarity_map():
    return render_template('wip.html', title='Similarity map',
                           description='Explore players with similar stats using K-means clustering.')
