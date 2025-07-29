/**
 * Documents Page Component for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Search, Filter, Download, Eye, Calendar, User, FileText } from 'lucide-react';
import { documentsAPI, coursesAPI } from '../lib/api';

const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCourse, setSelectedCourse] = useState('');
  const [sortBy, setSortBy] = useState('recent');

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [searchTerm, selectedCourse, sortBy]);

  const loadCourses = async () => {
    try {
      const coursesData = await coursesAPI.getAll();
      setCourses(coursesData);
    } catch (error) {
      console.error('Error loading courses:', error);
    }
  };

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedCourse) params.course = selectedCourse;
      
      const documentsData = await documentsAPI.getAll(params);
      
      // Sort documents
      let sortedDocuments = [...documentsData];
      switch (sortBy) {
        case 'recent':
          sortedDocuments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
          break;
        case 'popular':
          sortedDocuments.sort((a, b) => b.download_count - a.download_count);
          break;
        case 'title':
          sortedDocuments.sort((a, b) => a.title.localeCompare(b.title));
          break;
        default:
          break;
      }
      
      setDocuments(sortedDocuments);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleCourseChange = (value) => {
    setSelectedCourse(value === 'all' ? '' : value);
  };

  const handleSortChange = (value) => {
    setSortBy(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const DocumentCard = ({ document }) => (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1">
            <CardTitle className="text-lg line-clamp-2">{document.title}</CardTitle>
            <CardDescription className="line-clamp-2">
              {document.description || 'Aucune description disponible'}
            </CardDescription>
          </div>
        </div>
        <div className="flex items-center space-x-2 flex-wrap gap-2">
          <Badge variant="secondary">{document.course_domain}</Badge>
          <span className="text-sm text-muted-foreground flex items-center">
            <FileText className="h-3 w-3 mr-1" />
            {document.file_size_mb} MB
          </span>
          <span className="text-sm text-muted-foreground flex items-center">
            <Download className="h-3 w-3 mr-1" />
            {document.download_count}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span className="flex items-center">
              <User className="h-3 w-3 mr-1" />
              {document.uploaded_by_username}
            </span>
            <span className="flex items-center">
              <Calendar className="h-3 w-3 mr-1" />
              {formatDate(document.created_at)}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <Button size="sm" asChild className="flex-1">
              <Link to={`/documents/${document.id}`} className="flex items-center justify-center">
                <Eye className="h-4 w-4 mr-1" />
                Voir
              </Link>
            </Button>
            <Button size="sm" variant="outline" asChild>
              <a 
                href={documentsAPI.download(document.id)} 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center"
              >
                <Download className="h-4 w-4 mr-1" />
                Télécharger
              </a>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const DocumentSkeleton = () => (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <div className="flex space-x-2">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-5 w-16" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex justify-between">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-20" />
          </div>
          <div className="flex space-x-2">
            <Skeleton className="h-8 flex-1" />
            <Skeleton className="h-8 w-24" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Parcourir les cours</h1>
          <Button asChild>
            <Link to="/upload">Partager un cours</Link>
          </Button>
        </div>
        <p className="text-muted-foreground">
          Découvrez et téléchargez des cours PDF partagés par la communauté
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher des cours..."
                value={searchTerm}
                onChange={handleSearchChange}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedCourse || 'all'} onValueChange={handleCourseChange}>
              <SelectTrigger>
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Tous les domaines" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les domaines</SelectItem>
                {courses.map((course) => (
                  <SelectItem key={course.id} value={course.id.toString()}>
                    {course.name} ({course.documents_count})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={sortBy} onValueChange={handleSortChange}>
              <SelectTrigger>
                <SelectValue placeholder="Trier par" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">Plus récents</SelectItem>
                <SelectItem value="popular">Plus téléchargés</SelectItem>
                <SelectItem value="title">Titre (A-Z)</SelectItem>
              </SelectContent>
            </Select>

            <div className="text-sm text-muted-foreground flex items-center">
              {loading ? (
                <Skeleton className="h-4 w-24" />
              ) : (
                `${documents.length} document${documents.length > 1 ? 's' : ''} trouvé${documents.length > 1 ? 's' : ''}`
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          Array.from({ length: 6 }).map((_, index) => (
            <DocumentSkeleton key={index} />
          ))
        ) : documents.length > 0 ? (
          documents.map((document) => (
            <DocumentCard key={document.id} document={document} />
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Aucun document trouvé</h3>
            <p className="text-muted-foreground mb-4">
              Essayez de modifier vos critères de recherche ou de filtrage
            </p>
            <Button asChild>
              <Link to="/upload">Partager le premier cours</Link>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentsPage;

