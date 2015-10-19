import os.path
import sys, getopt

class HMMTagger:

	priorprobability = {}
	likelihood = {}
	least_likelihood = 1.0
	taglist = {}

# CREATING TABLES FROM CORPORA FILES
	def increment_occurrence(self,table, key1, key2):
		# INSERT word and/or word-tag occurence cells into likelihood, 
		# or insert tag and/or tag-preTag occurence cells into priorprobability
		if key1 not in table:
			table[key1] = {"occurences": 0, key2: 0}
		elif key2 not in table[key1]:
			table[key1][key2] = 0

		# INCREMENT table values
		table[key1]["occurences"] += 1
		table[key1][key2] += 1

	def add_likelihood_occurrence(self, word, tag):
		
		self.increment_occurrence(self.likelihood, word, tag)
		
		# READJUST least likelihood for unfound words
		occurencesOfTag = float(self.likelihood[word][tag])
		occurencesOfWord = float(self.likelihood[word]["occurences"])
		likeliness = (occurencesOfTag / occurencesOfWord)
		if self.least_likelihood > likeliness:
			self.least_likelihood = likeliness


	def add_priorprobability_occurence(self, tag, prevTag):
		self.increment_occurrence(self.priorprobability, tag, prevTag)


	def construct_tables_from_tagged_corpora(self, filecorpora, table="both"):
		f = open(filecorpora, "r")
		corpora = f.read().split("\n")
		f.close()

		prevTag = ""
		for line in corpora:
			line = line.strip(' \t\n\r').split("\t")

			if len(line) < 2:
				tag = ""
			else:
				token = line[0]
				tag = line[1]

				if token != "" and table != "priorprobability":
					self.add_likelihood_occurrence(token, tag)

			if table != "likelihood":
				self.add_priorprobability_occurence(tag, prevTag)

			self.taglist[tag] = True

			prevTag = tag





# TABLE FILE FUNCTIONS - STORING LIKELIHOOD AND PRIOR PRIORITY ON DISK
# OUPUT TABLES TO TABLE FILES
	def output_to_filehandler(self, table, filehandle, delimiter="="):
		# in new file
		# word    \t    occurence=#, tag1=#, tag2=#
		# word key will be separated from occurrences and tag by \t
		# the occurences and tag data will be split by comma and space ", "
		
		for key1 in table:
			line = key1 + "\t"

			data = []
			for key2 in table[key1]:
				data.append(key2 + delimiter + str(table[key1][key2]))

			line += ", ".join(data) + "\n"

			filehandle.write(line)


	def output_likelihood_to_file(self, likelihood_output, delimiter="="):
		lfile = open(likelihood_output, "w")

		lfile.write("least_likelihood=" + str(self.least_likelihood) + "\n")
		self.output_to_filehandler(self.likelihood, lfile,delimiter=delimiter)

		lfile.close()

	def output_priorprob_to_file(self, priorprobability_output, delimiter="="):
		ppfile = open(priorprobability_output, "w")

		self.output_to_filehandler(self.priorprobability, ppfile,delimiter=delimiter)

		ppfile.close()

	def output_tables_to_files(self, likelihood_output, priorprobability_output, delimiter="="):
		self.output_likelihood_to_file(likelihood_output,delimiter=delimiter)
		self.output_priorprob_to_file(priorprobability_output, delimiter=delimiter)



# CONSTUCTING TABLES FROM TABLE FILES
	def construct_from_table_file_lines(self, table, filelines, delimiter="="):
		for line in filelines:
			if line == "":
				continue

			line = line.split("\t")

			key1 = line[0]
			table[key1] = {}

			data = line[1].split(", ")
			for datum in data:
				datum = datum.split(delimiter)
			
				key2 = datum[0]
				val = int(datum[1])

				table[key1][key2] = val

				if key2 != "occurences":
					taglist[key2] = True



	def contruct_likelihood_from_table_file(self, likelihood_file, delimiter="="):
		lfile = open(likelihood_file, "r")

		llines = lfile.read().split("\n")

		least_likelihood_line = llines[0].split("=")
		self.least_likelihood = float(least_likelihood_line[1])
		llines[0] = ""

		self.construct_from_table_file_lines(self.likelihood, llines, delimiter)

		lfile.close()



	def construct_priorprob_from_table_file(self, priorprob_file, delimiter="="):
		ppfile = open(priorprob_file, "r")

		pplines = ppfile.read().split("\n")
		self.construct_from_table_file_lines(self.priorprobability, pplines, delimiter)

		ppfile.close()


	def construct_tables_from_table_files(self, likelihood_file, priorprob_file, delimiter="="):
		self.contruct_likelihood_from_table_file(likelihood_file, delimiter=delimiter)
		self.construct_priorprob_from_table_file(priorprob_file, delimiter=delimiter)




# GETTING PROBABILITIES
	def get_probability(self,table, key1, key2):
		if key1 not in table or key2 not in table[key1]:
			return 0

		key1_data = table[key1]

		key2_occurences = float(key1_data[key2])
		occurences = float(key1_data["occurences"])

		return key2_occurences / occurences


	def get_likelihood(self, word, tag):
		probability = self.get_probability(self.likelihood, word, tag)

		return probability if probability != 0 else self.least_likelihood

	def get_priorprobability(self, tag, prevTag):
		return self.get_probability(self.priorprobability, tag, prevTag)


# ACTUAL TAGGING
	def tag_file_corpora(self, filecorpora, systemOutput):
		f = open(filecorpora, "r")
		words = f.read().split("\n")
		f.close()

		out = open(systemOutput, "w")

		prevTag = ""

		for word in words:
			line = word

			highestScore = 0.0
			chosenTag = ""

			# FIND the highest scoring tag assignment based on tag or given previous tag
			if word in self.likelihood:
				for tag in self.likelihood[word]:
					score = self.get_likelihood(word, tag) * self.get_priorprobability(tag, prevTag)

					if highestScore < score:
						highestScore = score
						chosenTag = "\t" + tag
						
			# IF word not in likelihood table, make likelihood the least_likelihood for all possible tags
			else:
				for tag in self.taglist:
					score = self.least_likelihood * self.get_priorprobability(tag, prevTag)

					if highestScore < score:
						highestScore = score
						chosenTag = "\t" + tag


			out.write(line + chosenTag + "\n")

		out.close()

def main(argv):

	if len(argv) < 3:
		print("Need 3 file names: <file to make tables from> <file to tag> <name of system output file>")
		sys.exit(1)

	makeTableFrom = argv[0]
	toTagFile = argv[1]
	systemOutput = argv[2]

	tagger = HMMTagger()
	tagger.construct_tables_from_tagged_corpora(makeTableFrom)
	tagger.tag_file_corpora(toTagFile, systemOutput)

	if len(argv) > 3:
		answerKey = argv[3]
		os.system("java -classpath . POSScorer "+systemOutput+" "+answerKey)

if __name__ == "__main__":
   main(sys.argv[1:])



# tagger = HMMTagger()
# tagger.construct_tables_from_tagged_corpora("Homework4_corpus/POSData/training.pos")
# tagger.tag_file_corpora("Homework4_corpus/POSData/development.text")