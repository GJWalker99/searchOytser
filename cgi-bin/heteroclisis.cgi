#!/usr/bin/perl -w

# heteroclisis.cgi: script that looks up entries in the heteroclisis database
# Revised from qtclsh version, Raphael Finkel, 9/2020

use strict;
use HTML::Template;
use CGI qw/:standard -utf8 -debug/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);

my $html = HTML::Template->new(
        utf8 => 1,
        filename => 'heteroclisis.template',
        );

my $query = param('query') || '';

my $qddb = '/opt/hsdi/qddb/bin/qedit';
my $database = '/homes/raphael/databases/heteroclisis';
$html->param(query => $query);

if ($query eq '') {
	$html->param(haveResult => 0);
    print "Content-Type: text/html; charset=utf-8\n\n";
	print $html->output();
} else {
	$query =~ s/[<>\&'";\[\]\(\)\\]//g; # remove suspicious characters
	$query =~ /^(.*)$/; # untaint
	$query = $1;
	my $command = "$qddb l $database $query";
	# print "Command: [$command]\n";
	my $result = `$command`;
	my @results = ();
	for my $entry (split(/\n\n/, $result)) {
		my @rows; # table rows
		for my $line (split /\n/, $entry) {
			next if $line =~ /\$NUMBER\$/;
			$line =~ /^(\w+) = "(.*)"$/;
			my ($attribute, $value) = ($1, $2);
			$value =~ s/\\"/"/g;
			if ($attribute eq 'Lexeme_ID') {
				$attribute = 'Paradigm';
				my $fileName = "paradigm.$value.html";
				if (-r $fileName) {
					$value = "<a href='paradigm.$value.html'>chart</a>";
				} else {
					$value = "no chart available";
				}
			} else {
				$attribute =~ s/_/ /g;
				$value =~ s/($query)/"<span class='result'>$1<\/span>"/ieg;
			}
			push @rows, {entry =>
				"<td class='attribute'>$attribute</td><td>$value</td>"};
		} # each line of the entry
		push @results, {values => \@rows};
	} # each entry
	$html->param(results => \@results);

    print "Content-Type: text/html; charset=utf-8\n\n";
	# $html->param(result => $result);
	$html->param(haveResult => 1);
	print $html->output();
} # there is a query
